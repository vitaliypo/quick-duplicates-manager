import os
import random
import subprocess
import sys  # needed to pass arvg (cmd arguments) to QApplication
import threading
import time
from collections import Counter
from operator import lt, gt

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QTableView, QMessageBox
from send2trash import send2trash

from GUI import design
from data_model import CloneSpyResultsReader, TableModel, Column, Action, ValidationError, ValidationErrorType


def get_duplicates_list(filepath):
    reader = CloneSpyResultsReader(filepath)
    duplicates = reader.reformat_data_to_model()
    return duplicates


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):

    nthreads = 1

    def __init__(self, results_file_path="./resources/CloneSpyResult.txt"):

        super().__init__()
        # init design
        self.setupUi(self)

        # tableview setting up
        self.load_results_to_tableview(results_file_path)

        # add actions to buttons
        self.OpenResults.triggered.connect(self.browse_results_file)
        self.actionDelete_sibling_duplicates.triggered.connect(self.mark_siblings_delete)
        self.actionHardlink_sibling_duplicates.triggered.connect(self.mark_siblings_hardlink)
        self.pushButton_2.clicked.connect(self.start_files_processing)
        self.process_files_thread = None
        # self.files_processor_worker = None
        self.buildWorker(0)
        self.works = [0]

        self.btn_next_error.clicked.connect(self.select_next_error_row)
        self.btn_previous_error.clicked.connect(self.select_previous_error_row)
        self.btn_next_group.clicked.connect(self.select_next_group_without_action)
        self.btn_previous_group.clicked.connect(self.select_previous_group_without_action)
        self.tableView.selectionModel().selectionChanged.connect(self.refresh_current_error_message)
        # self.pushButton_2.clicked.connect(self.start_files_processing)

        QtWidgets.QShortcut(QtCore.Qt.Key_D, self.tableView, self.grab_keypress_delete)
        QtWidgets.QShortcut(QtCore.Qt.Key_H, self.tableView, self.grab_keypress_hardlink)
        QtWidgets.QShortcut(QtCore.Qt.Key_S, self.tableView, self.grab_keypress_source_for_hardlink)
        QtWidgets.QShortcut(QtCore.Qt.Key_N, self.tableView, self.grab_keypress_clear_action)
        QtWidgets.QShortcut(QtCore.Qt.Key_O, self.tableView, self.find_and_open_single_file_location)
        QtWidgets.QShortcut(QKeySequence('Ctrl+O'), self.tableView, self.find_and_open_all_locations_in_current_group)

        # pre-configured question window to always have reference to it
        self.files_exterminated_question_window = QMessageBox(QMessageBox.NoIcon, 'Warning!', 'Message')
        self.files_exterminated_question_window.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        self.files_exterminated_question_window.setDefaultButton(QMessageBox.No)

    def load_results_to_tableview(self, file_path_string):
        # tableview setting up
        data = get_duplicates_list(file_path_string)

        # dict to store hardlink and source pairs
        self.hardlink_index_to_source_index = dict()

        # assign model to view
        # current_errors passed to TableModel only to set red color of row text when row causes error
        self.current_errors = list()
        self.groups_without_action_first_row_number = set()
        self.model = TableModel(data, self.current_errors)
        self.tableView.setModel(self.model)

        self.all_groups_amount = self.model.get_amount_of_groups()
        self.groups_have_actions_label.setText("Groups have actions: 0 of " + str(self.all_groups_amount))

        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        QTableView.resizeColumnsToContents(self.tableView)

    def browse_results_file(self):
        chosen_file = QtWidgets.QFileDialog.getOpenFileName(self, "Choose CloneSpy results file")
        file = chosen_file[0]
        self.load_results_to_tableview(file)

    def refresh_current_error_message(self):
        current_error_str = None
        selected_rows = self.tableView.selectedIndexes()
        if len(self.current_errors) > 0 and len(selected_rows) > 0:
            # check if row has error
            for error in self.current_errors:
                if error.row_causing_the_error == selected_rows[0].row():
                    current_error_str = error.error_type.value
                    break
            if current_error_str is not None:
                self.field_current_error.setEnabled(True)
                self.field_current_error.setText(current_error_str)
                return
        self.field_current_error.setText("")
        self.field_current_error.setEnabled(False)

    def select_previous_group_without_action(self):
        self.tableView.setFocus()
        # make sure to not change values of errors_list because it's a shallow copy
        errors_list = self.current_errors.copy()
        errors_list.reverse()
        self.select_error_row(lt, errors_list)

    def select_next_group_without_action(self):
        self.tableView.setFocus()
        self.select_error_row(gt, self.current_errors)

    def select_previous_error_row(self):
        self.tableView.setFocus()
        # make sure to not change values of errors_list because it's a shallow copy
        errors_list = self.current_errors.copy()
        errors_list.reverse()
        self.select_error_row(lt, errors_list)

    def select_next_error_row(self):
        self.tableView.setFocus()
        self.select_error_row(gt, self.current_errors)

    def select_error_row(self, comparison_operator, errors_list):
        error_row_to_set = None
        if len(errors_list) == 1:
            error_row_to_set = errors_list[0].row_causing_the_error
        elif len(errors_list) > 1:
            current_row = self.tableView.currentIndex().row()
            for error in errors_list:
                if comparison_operator(error.row_causing_the_error, current_row):
                    error_row_to_set = error.row_causing_the_error
                    break
        if error_row_to_set is None:
            error_row_to_set = errors_list[0].row_causing_the_error
        self.tableView.selectRow(error_row_to_set)

    def refresh_errors_list(self, autocomplete_actions=True):
        # todo refresh errors of only changed group instead of all groups (whole table)?
        self.current_errors.clear()
        amount_of_groups = self.all_groups_amount
        row_to_start_next_search = 0
        for group in range(1, amount_of_groups + 1):
            indexes_of_current_group = self.model.find_indexes_of_value(Column.Group.index, group,
                                                                        row_to_start_next_search)
            # save it to start searching from this row in the next iteration
            row_to_start_next_search = indexes_of_current_group[-1].row() + 1
            actions = list()
            index_to_action = dict()
            for group_index in indexes_of_current_group:
                action_index = self.model.createIndex(group_index.row(), Column.Action.index)
                actions.append(action_index.data(Qt.DisplayRole))
                index_to_action[group_index] = action_index.data(Qt.DisplayRole)
            counter = Counter(actions)

            # TC07
            if counter.get(Action.source.value, 0) > 1:
                error_to_raise = ValidationErrorType.more_than_one_source_in_group
                action_to_find = Action.source
                row_causing_error = None
                for key, value in index_to_action.items():
                    if value == action_to_find.value:
                        row_causing_error = key.row()
                        break
                new_error = ValidationError(error_to_raise, row_causing_error)
                self.current_errors.append(new_error)

            # TC01-2, TC01-3
            if counter.get(Action.none) == 1:
                action_to_assign = None
                error_to_raise = None
                if counter.get(Action.hardlink.value, 0) > 0 and counter.get(Action.source.value) is None:
                    action_to_assign = Action.source
                    error_to_raise = ValidationErrorType.source_for_hardlink_absence
                elif counter.get(Action.source.value, 0) == 1 and counter.get(
                        Action.hardlink.value) is None:  # todo check if should be == 1 instead of > 0
                    action_to_assign = Action.hardlink
                    error_to_raise = ValidationErrorType.hardlink_absence
                if action_to_assign is not None:
                    row_to_change = 0
                    row_causing_error = 0
                    for key, value in index_to_action.items():
                        if value is Action.none:
                            row_to_change = key.row()
                        else:
                            row_causing_error = key.row()
                    index_of_action_to_change = self.model.createIndex(row_to_change, Column.Action.index)
                    if autocomplete_actions:
                        self.assign_action_to_row(action_to_assign.value, index_of_action_to_change)
                    else:
                        new_error = ValidationError(error_to_raise, row_causing_error)
                        self.current_errors.append(new_error)

            # TC03 + TC06
            if counter.get(Action.none, 0) > 1:
                # collect groups without actions to one list
                if counter.get(Action.source.value, 0) == 0 \
                        and counter.get(Action.hardlink.value, 0) == 0 \
                        and counter.get(Action.delete.value, 0) == 0:
                    self.groups_without_action_first_row_number.add(indexes_of_current_group[0].row())

                action_exists = None
                error_type = None
                if counter.get(Action.hardlink.value, 0) > 0 and counter.get(Action.source.value) is None:
                    action_exists = Action.hardlink
                    error_type = ValidationErrorType.source_for_hardlink_absence
                elif counter.get(Action.source.value, 0) > 0 and counter.get(Action.hardlink.value) is None:
                    action_exists = Action.source
                    error_type = ValidationErrorType.hardlink_absence

                if action_exists is not None and error_type is not None:
                    row_causing_error = 0
                    for key, value in index_to_action.items():
                        if value == action_exists.value:
                            row_causing_error = key.row()
                            break
                    for error in self.current_errors:
                        if error.row_causing_the_error == row_causing_error:
                            return
                    new_error = ValidationError(error_type, row_causing_error)
                    self.current_errors.append(new_error)

            # TC05-1, TC05-2
            if counter.get(Action.none, 0) == 0:
                error_to_raise = None
                action_to_find = None
                if counter.get(Action.hardlink.value, 0) >= 1 and counter.get(Action.source.value, 0) == 0:
                    error_to_raise = ValidationErrorType.source_for_hardlink_absence
                    action_to_find = Action.hardlink
                if counter.get(Action.hardlink.value, 0) == 0 and counter.get(Action.source.value, 0) == 1:
                    error_to_raise = ValidationErrorType.hardlink_absence
                    action_to_find = Action.source
                if error_to_raise is not None:
                    row_causing_error = None
                    for key, value in index_to_action.items():
                        if value == action_to_find.value:
                            row_causing_error = key.row()
                            break
                    new_error = ValidationError(error_to_raise, row_causing_error)
                    self.current_errors.append(new_error)

            if counter.get(Action.source.value, 0) > 0 \
                    or counter.get(Action.hardlink.value, 0) > 0 \
                    or counter.get(Action.delete.value, 0) > 0:
                self.groups_without_action_first_row_number.discard(indexes_of_current_group[0].row())

        new_error_label_string = "Errors found: " + str(len(self.current_errors))
        self.label_errors_count.setText(new_error_label_string)
        errors_exist = len(self.current_errors) > 0
        self.btn_next_error.setEnabled(errors_exist)
        self.btn_previous_error.setEnabled(errors_exist)
        if errors_exist:
            self.label_errors_count.setStyleSheet("color: red")
        else:
            self.label_errors_count.setStyleSheet("color: black")
        self.current_errors.sort(key=lambda element: element.row_causing_the_error)
        self.refresh_current_error_message()

        groups_have_action = self.all_groups_amount - len(self.groups_without_action_first_row_number)
        current_groups_label_text = "Groups have actions: " + str(groups_have_action) + " of " \
                                    + str(self.all_groups_amount)
        self.groups_have_actions_label.setText(current_groups_label_text)
        if len(self.groups_without_action_first_row_number) > 0:
            self.btn_previous_group.setEnabled(True)
            self.btn_next_group.setEnabled(True)
        else:
            self.btn_previous_group.setEnabled(False)
            self.btn_next_group.setEnabled(False)

    def mark_siblings(self, action):
        # print(action)
        indexes = self.tableView.selectedIndexes()
        if indexes:
            path_index = indexes[1]
            path = self.model.data(path_index, Qt.EditRole)
            parent = path.parent
            print(parent)
            # file = self.model.data(path_index, Qt.DisplayRole)
            for iteration in range(self.model.rowCount(0)):
                index = self.model.createIndex(iteration, 1)
                iteration_path = self.model.data(index, Qt.EditRole)
                iteration_parent = iteration_path.parent
                if parent == iteration_parent:
                    index_of_action_to_set = self.model.createIndex(iteration, Column.Action.index)
                    self.assign_action_to_row(action, index_of_action_to_set)
                    # self.model.setData(set_index, action)

    def mark_siblings_delete(self):
        self.mark_siblings(Action.delete.value)
        self.refresh_errors_list()

    def mark_siblings_hardlink(self):
        self.mark_siblings(Action.hardlink)
        self.refresh_errors_list()

    def grab_keypress_delete(self):
        indexes_selected = self.tableView.selectedIndexes()
        if indexes_selected:
            self.assign_action_to_current_row(Action.delete, indexes_selected)
            self.refresh_errors_list()

    def grab_keypress_source_for_hardlink(self):
        indexes_selected = self.tableView.selectedIndexes()
        if indexes_selected:
            self.assign_action_to_current_row(Action.source, indexes_selected)
            self.refresh_errors_list()

    def grab_keypress_hardlink(self):
        # todo check if files are on NTFS system
        # todo check if files are on the same volume

        # current_row = self.tableView.currentIndex().row()

        # current_group = self.model.createIndex(current_row, Column.Group.index).data(Qt.DisplayRole)
        # indexes_of_current_group = self.model.find_indexes_of_value(Column.Group.index, current_group)

        # if len(indexes_of_current_group) > 2:

        # paths = list()
        # drives = set()
        # for index in indexes_of_current_group:
        #     path = self.model.createIndex(index.row(), Column.Path.index).data(Qt.EditRole)
        #     paths.append(path)
        # for path in paths:
        #     drives.add(path.drive)
        indexes_selected = self.tableView.selectedIndexes()
        if indexes_selected:
            self.assign_action_to_current_row(Action.hardlink, indexes_selected)
            self.refresh_errors_list()

    def grab_keypress_clear_action(self):
        indexes_selected = self.tableView.selectedIndexes()
        if indexes_selected:
            self.assign_action_to_current_row(Action.none, indexes_selected)
            self.refresh_errors_list(False)

    def assign_action_to_current_row(self, action, selected_indexes):
        action_row_index = selected_indexes[Column.Action.index]
        self.assign_action_to_row(action, action_row_index)

    def assign_action_to_row(self, action, action_row_index):
        self.model.setData(action_row_index, action)

    def find_and_open_single_file_location(self):
        path_string = self.find_selected_file_location()
        self.open_file_location(path_string)

    def open_file_location(self, path_string):
        print("Opening: " + path_string)
        subprocess.Popen(r'explorer /select,"' + path_string + '"')

    def find_selected_file_location(self):
        current_row = self.tableView.currentIndex().row()
        path_string = self.find_file_location(current_row)
        return path_string

    def find_file_location(self, row):
        path_index = self.model.createIndex(row, Column.Path.index)
        path_string = path_index.data(Qt.DisplayRole)
        return path_string

    def find_and_open_all_locations_in_current_group(self):
        current_row = self.tableView.currentIndex().row()
        current_group = self.model.createIndex(current_row, Column.Group.index).data(Qt.DisplayRole)
        indexes_of_group = self.model.find_indexes_of_value(Column.Group.index, current_group)
        for index in indexes_of_group:
            path_string = self.find_file_location(index.row())
            self.open_file_location(path_string)

    def handleProgress(self, signal):
        """you can add any logic you want here,
        it will be executed in the main thread
        """
        index, progress = signal
        self.works[index] = progress
        rows = self.model.rowCount(0)
        value = progress / rows * 100
        # for work in self.works:
        #     value += work
        # value /= float(self.nthreads)
        # management of special cases
        if value > 100:
            # self.progressBar.hide()
            return
        self.progressBar.setValue(int(value))
        print('progress (ui) thread: %s  (value: %d)' % (threading.current_thread().name, value))

    def buildWorker(self, index):
        thread = QtCore.QThread()
        worker = FilesProcessor(index, self)
        worker.updateProgress.connect(self.handleProgress)
        # worker.startProcessing.connect(self.process_files)
        worker.moveToThread(thread)
        thread.started.connect(worker.work)
        worker.finished.connect(thread.quit)
        # QtCore.QMetaObject.connectSlotsByName(self)
        self.process_files_thread = thread
        self.files_processor_worker = worker

    # def runThreads(self):
    #     for thread in self.process_files_thread:
    #         thread.start()

    def start_files_processing(self):
        # self.buildWorker(0)
        self.process_files_thread.start()

    # def process_files(self):
    #     print("process_files started")
    #     groups_exterminated = self.groups_exterminated()
    #     if len(groups_exterminated) > 0:
    #         print(groups_exterminated)
    #         groups_exterminated_strings = list()
    #         for group in groups_exterminated:
    #             groups_exterminated_strings.append(str(group))
    #         message = "All members of following ranges will be removed\n" + "\n".join(
    #             groups_exterminated_strings) + "\nContinue?"
    #         self.files_exterminated_question_window.setText(message)
    #         print(self.files_exterminated_question_window)
    #         answer = self.files_exterminated_question_window.exec()
    #         # self.files_exterminated_question_window.show()
    #         print(self.files_exterminated_question_window)
    #         print(answer)
    #         if answer == QMessageBox.Yes:
    #             pass
    #         else:
    #             return
    #
    #     row_count = self.model.rowCount(0)
    #     for row in range(row_count):
    #         processed_index = self.model.createIndex(row, Column.Processed.index)
    #         processed_value = self.model.data(processed_index, Qt.EditRole)
    #         if not processed_value:
    #             index = self.model.createIndex(row, Column.Action.index)
    #             action = self.model.data(index, Qt.DisplayRole)
    #             if action is not Action.none:
    #                 if action == Action.delete:
    #                     print("Delete file", row)
    #                     file = self.model.createIndex(row, Column.Path.index).data(Qt.DisplayRole)
    #                     send2trash(file)
    #                     self.mark_processed(row)
    #
    #                 elif action == Action.hardlink:
    #                     print("Hardlink file")
    #                     expected_path_index = self.model.createIndex(row, Column.Path.index)
    #                     source_for_hardlink_index = self.hardlink_index_to_source_index[expected_path_index]
    #                     hardlink_path = expected_path_index.data(Qt.EditRole)
    #                     source_for_hardlink_path = source_for_hardlink_index.data(Qt.EditRole)
    #                     send2trash(str(hardlink_path))
    #                     os.link(source_for_hardlink_path, hardlink_path)
    #                     self.mark_processed(row)
    #                     self.mark_processed(source_for_hardlink_index.row())

    def mark_processed(self, current_row):
        index = self.model.createIndex(current_row, 6)
        self.model.setData(index, True)

    def groups_exterminated(self):
        groups_to_be_exterminated = list()
        groups_last_row_index = self.model.createIndex(self.model.rowCount(0) - 1, Column.Group.index)
        groups_count = self.model.data(groups_last_row_index, Qt.DisplayRole)
        last_index_recorded_row = 0
        for group_number in range(1, groups_count + 1):
            index_to_action = dict()
            hardlink_indexes = list()
            source_for_hardlink_index = None
            indexes_of_group = self.model.find_indexes_of_value(Column.Group.index, group_number,
                                                                last_index_recorded_row)
            if len(indexes_of_group) != 0:
                actions = list()
                processed_values = list()
                for index in indexes_of_group:
                    action_index = self.model.createIndex(index.row(), Column.Action.index)
                    processed_value_index = self.model.createIndex(index.row(), Column.Processed.index)
                    action = self.model.data(action_index, Qt.EditRole)
                    index_to_action[action_index] = action
                    actions.append(action)
                    processed_values.append(processed_value_index.data(Qt.DisplayRole))

                # todo add more cases/combinations of actions
                if Action.none not in actions and False in processed_values:
                    groups_to_be_exterminated.append(group_number)

                for action_index, action in index_to_action.items():
                    if action == Action.hardlink:
                        hardlink_path_index = self.model.createIndex(action_index.row(), Column.Path.index)
                        # hardlink_path = hardlink_path_index.data(Qt.EditRole)
                        hardlink_indexes.append(hardlink_path_index)
                    elif action == Action.source:
                        source_for_hardlink_path_index = self.model.createIndex(action_index.row(), Column.Path.index)
                        # source_for_hardlink_path = source_for_hardlink_path_index.data(Qt.EditRole)
                        source_for_hardlink_index = source_for_hardlink_path_index

                if len(hardlink_indexes) > 0 and source_for_hardlink_index is not None:
                    for hardlink_index in hardlink_indexes:
                        self.hardlink_index_to_source_index[hardlink_index] = source_for_hardlink_index

                last_index_recorded_row = indexes_of_group[-1].row()
        return groups_to_be_exterminated


class FilesProcessor(QtCore.QObject):
    """the worker for a threaded process;
    (this is created in the main thread and
    then moved to a QThread, before starting it)
    """

    updateProgress = QtCore.pyqtSignal(tuple)
    finished = QtCore.pyqtSignal(int)
    # todo add FAILEd signal to avoid UI hanging on errors
    # startProcessing = QtCore.pyqtSignal()

    def __init__(self, index, app):
        super(FilesProcessor, self).__init__()
        # store the Worker index (for thread tracking
        # and to compute the overall progress)
        self.id = index
        self.link_to_app_class = app

    def work(self):
        # print("Work started")
        groups_exterminated = self.link_to_app_class.groups_exterminated()
        # ask user for confirmation in case if some duplicate groups will be removed completely
        if len(groups_exterminated) > 0:
            print(groups_exterminated)
            groups_exterminated_strings = list()
            for group in groups_exterminated:
                groups_exterminated_strings.append(str(group))
            message = "All members of following ranges will be removed\n" + "\n".join(
                groups_exterminated_strings) + "\nContinue?"
            self.link_to_app_class.files_exterminated_question_window.setText(message)
            print(self.link_to_app_class.files_exterminated_question_window)
            answer = self.link_to_app_class.files_exterminated_question_window.exec()
            # self.link_to_app_class.files_exterminated_question_window.show()
            print(self.link_to_app_class.files_exterminated_question_window)
            print(answer)
            if answer == QMessageBox.Yes:
                pass
            else:
                return

        row_count = self.link_to_app_class.model.rowCount(0)
        rows_walked = 0
        self.updateProgress.emit((self.id, rows_walked))
        for row in range(row_count):
            time.sleep(random.random() * .2)  # testing/dev imitation of work, todo remove in prod
            processed_index = self.link_to_app_class.model.createIndex(row, Column.Processed.index)
            processed_value = self.link_to_app_class.model.data(processed_index, Qt.EditRole)
            if not processed_value:
                index = self.link_to_app_class.model.createIndex(row, Column.Action.index)
                action = self.link_to_app_class.model.data(index, Qt.EditRole)
                if action is not Action.none:
                    if action == Action.delete:
                        print("Delete file", row)
                        file = self.link_to_app_class.model.createIndex(row, Column.Path.index).data(Qt.DisplayRole)
                        send2trash(file)
                        self.link_to_app_class.mark_processed(row)

                    elif action == Action.hardlink:
                        print("Hardlink file")
                        expected_path_index = self.link_to_app_class.model.createIndex(row, Column.Path.index)
                        source_for_hardlink_index = \
                            self.link_to_app_class.hardlink_index_to_source_index[expected_path_index]
                        hardlink_path = expected_path_index.data(Qt.EditRole)
                        source_for_hardlink_path = source_for_hardlink_index.data(Qt.EditRole)
                        send2trash(str(hardlink_path))
                        os.link(source_for_hardlink_path, hardlink_path)
                        self.link_to_app_class.mark_processed(row)
                        self.link_to_app_class.mark_processed(source_for_hardlink_index.row())
            rows_walked += 1
            self.updateProgress.emit((self.id, rows_walked))
            # print("work cycle finished")
        self.finished.emit(1)


def main():
    app = QtWidgets.QApplication(sys.argv)  # new QApplication object
    window = ExampleApp()
    window.show()  # show the window
    app.exec_()  # run the app


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys.excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':  # If we run the file directly and not import it
    # The next code block is needed to correctly print exceptions to standard
    # output because it didn't work by default for some reason
    # Back up the reference to the exceptionhook
    # sys._excepthook = sys.excepthook
    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    main()
