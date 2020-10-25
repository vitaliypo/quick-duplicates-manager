import os
import pathlib
# from distutils.dir_util import copy_tree
from shutil import rmtree, copytree

import pytest
import winshell
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from data_model import Column, Action, ValidationErrorType, ValidationError
from main import ExampleApp


class TestClass:
    # TODO: refactoring, make parts of tests reusable
    # TODO: remove old tests which are not working/covered by new ones
    def setup_method(self):
        base = ".\\resources\\test_data"
        data_source = base + "\\source"
        tempdir = base + "\\temp_dir"
        try:
            rmtree(tempdir)
        except FileNotFoundError:
            pass

        copytree(data_source, tempdir)  # Throws file not found exception

        self.app = QApplication([])
        self.ui = ExampleApp(".\\resources\\CloneSpyResult.txt")
        self.menu = self.ui.menuBar()
        self.ui.show()
        QTest.qWaitForWindowExposed(self.ui)

    def teardown_method(self):
        rmtree(".\\resources\\test_data\\temp_dir")

    # todo check if this test should be left/removed/fixed
    @pytest.mark.parametrize("key, row, expected_action", [(Qt.Key_D, 0, "Delete"),
                                                           (Qt.Key_H, -1, "Hardlink"),
                                                           (Qt.Key_U, 0, None)
                                                           ])
    def test_if_key_presses_registered_as_action(self, row_chosen, qtbot, key, row, expected_action):
        # GIVEN main window displayed and a row selected - handled by fixture
        # WHEN action key pressed
        # self.mark_rows_with_actions(row, key)
        QTest.keyPress(self.ui, key, Qt.NoModifier, 100)
        QTest.keyRelease(self.ui, key)
        # THEN Action column value changed to action
        data = list()
        for i in range(7):
            index = self.ui.model.createIndex(row, i)
            data.append(index.data(Qt.DisplayRole))
        assert data[Column.Action.index] == expected_action
        assert data[Column.Processed.index] is False

    @pytest.fixture()
    def main_window_displayed(self, qtbot):
        qtbot.addWidget(self.ui)

    @pytest.fixture()
    def row_chosen(self, main_window_displayed, row):
        if row == -1:
            row = self.ui.model.rowCount(0) - 1
        self.ui.tableView.selectRow(row)

    # todo check if this test should be left/removed/fixed
    @pytest.mark.parametrize("key, row, expected_action, expected_processed", [(Qt.Key_D, 0, "Delete", True),
                                                                               (Qt.Key_H, -1, "Hardlink", True),
                                                                               (Qt.Key_U, 5, None, False)
                                                                               ])
    def test_processing_changes_table_values(self, row_chosen, qtbot, key, row, expected_action, expected_processed):
        # todo reuse same logic among tests
        # GIVEN actions assigned to some files
        QTest.keyPress(self.ui, key, Qt.NoModifier, 100)
        QTest.keyRelease(self.ui, key)
        data = list()
        for i in range(7):
            index = self.ui.model.createIndex(row, i)
            data.append(index.data(Qt.DisplayRole))
        assert data[Column.Action.index] == expected_action
        assert data[Column.Processed.index] is False
        # WHEN click Execute Action button
        QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)
        # THEN Processed set == True where Action is not empty
        data.clear()
        for i in range(7):
            index = self.ui.model.createIndex(row, i)
            data.append(index.data(Qt.DisplayRole))
        assert data[Column.Processed.index] == expected_processed



    # todo add groups of more than 2 members to test data
    # todo add tests for groups mentioned above
    # todo check if this test should be left/removed/fixed
    @pytest.mark.parametrize("group_to_mark, keys", [(1, [Qt.Key_D]),
                                                     (-1, [Qt.Key_D]),
                                                     (1, [Qt.Key_D, Qt.Key_H]),
                                                     (2, [Qt.Key_D, Qt.Key_H, Qt.Key_D])
                                                     ])
    def test_group_validations_popup_message_shown(self, main_window_displayed, group_to_mark, keys, qtbot):
        # GIVEN actions assigned to all members of some range
        if group_to_mark == -1:  # if group is -1 then take last group in the table
            last_index_row = self.ui.model.rowCount(0)-1
            last_group_value_index = self.ui.model.createIndex(last_index_row, Column.Group.index)
            group_to_mark = last_group_value_index.data(Qt.DisplayRole)

        indexes_of_group = self.ui.model.find_indexes_of_value(Column.Group.index, group_to_mark)
        if len(keys) == 1:
            for index in indexes_of_group:
                self.ui.tableView.selectRow(index.row())
                QTest.keyPress(self.ui, keys[0], Qt.NoModifier, 0)
                QTest.keyRelease(self.ui, keys[0])
                data = list()
                for i in range(7):
                    index = self.ui.model.createIndex(index.row(), i)
                    data.append(index.data(Qt.DisplayRole))
                # group = data[Column.Group.index]
                # assert data[Column.Action.index] == expected_action todo activate
                assert data[Column.Processed.index] is False
        else:
            for index, key in zip(indexes_of_group, keys):
                self.ui.tableView.selectRow(index.row())
                QTest.keyPress(self.ui, key, Qt.NoModifier, 0)
                QTest.keyRelease(self.ui, key)
                data = list()
                for i in range(7):
                    index = self.ui.model.createIndex(index.row(), i)
                    data.append(index.data(Qt.DisplayRole))
                # group = data[Column.Group.index]
                # assert data[Column.Action.index] == expected_action todo activate
                assert data[Column.Processed.index] is False

        # WHEN click Execute Action button
        QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)

        # THEN popup shown with ranges which will be fully removed
        # QTimer.singleShot(1000, handle_popup_waiting)
        assert self.ui.files_exterminated_question_window.isActiveWindow()
        assert self.ui.files_exterminated_question_window.isVisible()
        assert str(group_to_mark) in self.ui.files_exterminated_question_window.text()  # todo test proper format
        # WHEN clicked Cancel
        buttons = self.ui.files_exterminated_question_window.buttons()
        no_button = None
        yes_button = None
        for button in buttons:
            if 'No' in button.text():
                no_button = button
            elif 'Yes' in button.text():
                yes_button = button
        QTest.mouseClick(no_button, Qt.LeftButton)
        # THEN actions not executed and files not touched
        assert not self.ui.files_exterminated_question_window.isActiveWindow()
        assert not self.ui.files_exterminated_question_window.isVisible()
        # todo assert files exist
        # todo add validation of popup text
        # WHEN click Execute Action button again
        QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)
        # THEN popup shown with ranges which will be fully removed
        assert self.ui.files_exterminated_question_window.isActiveWindow()
        assert self.ui.files_exterminated_question_window.isVisible()
        # WHEN clicked Yes
        QTest.mouseClick(yes_button, Qt.LeftButton)
        # THEN actions applied to duplicates, files removed
        assert not self.ui.files_exterminated_question_window.isActiveWindow()
        assert not self.ui.files_exterminated_question_window.isVisible()
        # todo assert files not exist
        assert 1

    def mark_rows_with_keys(self, rows, keys):
        actions = self.convert_keys_to_actions(keys)
        for row, key, action in zip(rows, keys, actions):
            if row == -1:
                row = self.ui.model.rowCount(0) - 1
            self.ui.tableView.selectRow(row)
            QTest.keyPress(self.ui, key, Qt.NoModifier, 100)
            QTest.keyRelease(self.ui, key)
            data = list()
            for i in range(7):
                index = self.ui.model.createIndex(row, i)
                data.append(index.data(Qt.DisplayRole))
            # group = data[Column.Group.index]
            assert data[Column.Action.index] == action.value
            assert data[Column.Processed.index] is False

    def convert_keys_to_actions(self, keys):
        actions = list()
        for key in keys:
            if key == Qt.Key_D:
                actions.append(Action.delete)
            elif key == Qt.Key_H:
                actions.append(Action.hardlink)
            elif key == Qt.Key_S:
                actions.append(Action.source)
            elif key == Qt.Key_N:
                actions.append(Action.none)
        return actions

    def handle_question_window(self, accept, group):
        w = self.app.activeModalWidget()
        assert w.isVisible()
        window_text = w.text()
        assert str(group) in window_text

        no_button, yes_button = self.find_buttons()
        if accept:
            yes_button.click()
        else:
            no_button.click()

        assert not w.isVisible()

    def find_buttons(self):
        buttons = self.ui.files_exterminated_question_window.buttons()
        no_button = None
        yes_button = None
        for button in buttons:
            if 'No' in button.text():
                no_button = button
            elif 'Yes' in button.text():
                yes_button = button
        return no_button, yes_button

    def get_actions_in_group(self, group_number):
        group_indexes = self.ui.model.find_indexes_of_value(Column.Group.index, group_number)
        actions = self.get_actions_from_group_indexes(group_indexes)
        actions_objects = list()
        for action in actions:
            actions_objects.append(Action(action))
        return actions_objects

    def get_actions_from_group_indexes(self, group_indexes):
        actions = list()
        for group_index in group_indexes:
            action_index = self.ui.model.createIndex(group_index.row(), Column.Action.index)
            action = action_index.data(Qt.DisplayRole)
            actions.append(action)
        return actions

    def get_errors_for_group(self, group_number):
        indexes_of_group = self.ui.model.find_indexes_of_value(Column.Group.index, group_number)
        rows_of_group = (index.row() for index in indexes_of_group)
        errors = self.ui.current_errors.copy()
        errors_of_group = list()
        for error in errors:
            if error.row_causing_the_error in rows_of_group:
                errors_of_group.append(error)
        return errors_of_group

    def mark_group_with_keys(self, group, keys):
        indexes_of_group = self.ui.model.find_indexes_of_value(Column.Group.index, group)
        rows = (index.row() for index in indexes_of_group)
        self.mark_rows_with_keys(rows, keys)

    # todo fix this test or functionality
    @pytest.mark.parametrize("rows, keys, groups_in_prompt", [
        # TC04
        ([0, 1, 2], [Qt.Key_D, Qt.Key_D, Qt.Key_D], "1"),
        ([13, 14], [Qt.Key_D, Qt.Key_D], "5")
    ])
    def test_groups_extermination_popup_message_shown(self, main_window_displayed, rows, keys, groups_in_prompt, qtbot):
        # GIVEN actions assigned to all members of some group
        self.mark_rows_with_keys(rows, keys)

        # WHEN click Execute Action button
        QTimer.singleShot(1000, lambda: self.handle_question_window(False, groups_in_prompt))
        QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)

        # THEN popup shown with ranges which will be fully removed
        # WHEN clicked Cancel
        # THEN actions not executed and files not touched
        paths = list()
        indexes = self.ui.model.find_indexes_of_value(Column.Group.index, int(groups_in_prompt))
        for index in indexes:
            file_index = self.ui.model.createIndex(index.row(), Column.Path.index)
            path = file_index.data(Qt.EditRole)
            paths.append(path)
            assert os.path.isfile(path)

        # WHEN click Execute Action button again
        QTimer.singleShot(1000, lambda: self.handle_question_window(True, groups_in_prompt))
        QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)

        # THEN popup shown with ranges which will be fully removed

        # WHEN clicked Yes
        # THEN actions applied to duplicates, files removed
        for path in paths:
            assert not os.path.isfile(path)
            assert len(winshell.ShellRecycleBin().versions(str(path))) > 0

    @pytest.mark.parametrize("keys_to_assign, group_number", [
        # TC00
        ([], 1),
        # TC01
        ([Qt.Key_D, Qt.Key_D], 1),
        # TC02
        ([Qt.Key_D], 3)

    ])
    def test_positive_no_errors_assigned(self, main_window_displayed, qtbot,
                                         keys_to_assign, group_number):
        # GIVEN list of duplicates displayed
        # WHEN actions assigned to the group
        if len(keys_to_assign) > 0:
            indexes_of_group = self.ui.model.find_indexes_of_value(Column.Group.index, group_number)
            rows = (index.row() for index in indexes_of_group)
            self.mark_rows_with_keys(rows, keys_to_assign)

        # THEN there's no errors raised for the group
        errors = self.get_errors_for_group(group_number)
        assert len(errors) == 0

    @pytest.mark.parametrize("keys_to_assign, group_number, action_expected_from_autocompletion", [
        # TC01-2
        ([Qt.Key_H], 2, Action.source),
        ([Qt.Key_H, Qt.Key_D, Qt.Key_D, Qt.Key_D], 3, Action.source),
        # TC01-3
        ([Qt.Key_S], 2, Action.hardlink),
        ([Qt.Key_N, Qt.Key_D, Qt.Key_D, Qt.Key_S, Qt.Key_D], 3, Action.hardlink)
    ])
    def test_auto_completion_of_actions(self, main_window_displayed, qtbot,
                                        keys_to_assign, group_number,
                                        action_expected_from_autocompletion):
        # GIVEN duplicates displayed
        # WHEN actions assigned to rows
        indexes_of_group = self.ui.model.find_indexes_of_value(Column.Group.index, group_number)
        rows = (index.row() for index in indexes_of_group)
        self.mark_rows_with_keys(rows, keys_to_assign)

        # THEN there's no errors raised for the group
        errors = self.get_errors_for_group(group_number)
        assert len(errors) == 0
        # AND autocompletion added actions to the group
        actions = self.get_actions_in_group(group_number)
        assert action_expected_from_autocompletion in actions

    @pytest.mark.parametrize("keys_to_assign, group_number, error_type_expected, error_rownumber_expected", [
        # TC03
        ([Qt.Key_H, Qt.Key_D, Qt.Key_H], 3, ValidationErrorType.source_for_hardlink_absence, 5),
        # TC06
        ([Qt.Key_S, Qt.Key_D, Qt.Key_D], 3, ValidationErrorType.hardlink_absence, 5),
        # TC05-1
        ([Qt.Key_H, Qt.Key_D, Qt.Key_D, Qt.Key_D, Qt.Key_D], 3, ValidationErrorType.source_for_hardlink_absence, 5),
        # TC05-2
        ([Qt.Key_D, Qt.Key_D, Qt.Key_S, Qt.Key_D, Qt.Key_D], 3, ValidationErrorType.hardlink_absence, 7),
        # TC07
        ([Qt.Key_S, Qt.Key_D, Qt.Key_S], 3, ValidationErrorType.more_than_one_source_in_group, 5)
    ])
    def test_source_and_hardlink_errors_validation(self, main_window_displayed, qtbot,
                                                    keys_to_assign, group_number,
                                                    error_type_expected, error_rownumber_expected):
        # GIVEN duplicates displayed
        # WHEN actions assigned to rows
        self.mark_group_with_keys(group_number, keys_to_assign)
        # THEN new error generated and assigned to the row
        errors = self.get_errors_for_group(group_number)

        assert error_type_expected in (err.error_type for err in errors)
        assert error_rownumber_expected in (err.row_causing_the_error for err in errors)

    @pytest.mark.parametrize("keys_to_assign_1, group_number_1, error_row_1, keys_to_assign_2, group_number_2, error_row_2",
                             [
                                 ([Qt.Key_H, Qt.Key_D, Qt.Key_D], 1, 0, [Qt.Key_D, Qt.Key_D, Qt.Key_S], 3, 7),
                                 ([Qt.Key_H, Qt.Key_H, Qt.Key_D], 1, 0, [Qt.Key_D, Qt.Key_D, Qt.Key_S], 3, 7)
                             ]
                             )
    def test_errors_controls_behavior(self, main_window_displayed, qtbot,
                                      keys_to_assign_1,
                                      group_number_1,
                                      error_row_1,
                                      keys_to_assign_2,
                                      group_number_2,
                                      error_row_2):
        # GIVEN duplicates displayed
        # WHEN actions assigned to rows
        self.mark_group_with_keys(group_number_1, keys_to_assign_1)
        # THEN error counter changed
        assert self.ui.label_errors_count.text() == "Errors found: 1"
        # AND label color changed
        assert self.ui.label_errors_count.styleSheet() == "color: red"
        # AND row has red color
        error_row_1_index = self.ui.model.createIndex(error_row_1, 0)
        color1 = error_row_1_index.data(Qt.ForegroundRole)
        assert color1 == QtGui.QColor("red")
        # self.ui.model.data()
        # error_row_1

        # WHEN another actions assigned to another rows
        self.mark_group_with_keys(group_number_2, keys_to_assign_2)
        # THEN error counter changed
        assert self.ui.label_errors_count.text() == "Errors found: 2"
        # AND row has red color
        error_row_2_index = self.ui.model.createIndex(error_row_1, 0)
        color2 = error_row_2_index.data(Qt.ForegroundRole)
        assert color2 == QtGui.QColor("red")

        # AND navigation buttons can be used to go to next and previous errors
        next_error = self.ui.btn_next_error
        prev_error = self.ui.btn_previous_error
        QTest.mouseClick(prev_error, Qt.LeftButton)
        assert self.ui.tableView.currentIndex().row() == error_row_1
        QTest.mouseClick(prev_error, Qt.LeftButton)
        assert self.ui.tableView.currentIndex().row() == error_row_2
        QTest.mouseClick(next_error, Qt.LeftButton)
        assert self.ui.tableView.currentIndex().row() == error_row_1
        QTest.mouseClick(next_error, Qt.LeftButton)
        assert self.ui.tableView.currentIndex().row() == error_row_2

    @pytest.mark.parametrize("row_to_select, action", [
        (1, Action.delete),
        (6, Action.hardlink)
    ])
    def test_mark_siblings_actions(self, main_window_displayed, qtbot,
                                   row_to_select,
                                   action):
        # GIVEN some row selected
        self.ui.tableView.selectRow(row_to_select)
        row_path_index = self.ui.model.createIndex(row_to_select, Column.Path.index)
        # row_action_index = self.ui.model.createIndex(row_to_select, Column.Action.index)
        # row_action = row_action_index.data(Qt.DisplayRole)
        row_path = row_path_index.data(Qt.EditRole)
        row_path_parent = row_path.parent

        # WHEN some mark action triggered
        if action == Action.delete:
            trigger = self.ui.actionDelete_sibling_duplicates
        elif action == Action.hardlink:
            trigger = self.ui.actionHardlink_sibling_duplicates
        # elif action == Action.source:
            # action = self.ui.actionSource_sibling_duplicates
        # todo add Source mark action to gui and main method
        trigger.trigger()

        # THEN all rows from the same folder marked selected action
        #   get all the rows
        rowcount = self.ui.model.rowCount(0)
        # columncount = self.ui.model.columnCount()
        for rownum in range(rowcount):
            path_index = self.ui.model.createIndex(rownum, Column.Path.index)
            action_index = self.ui.model.createIndex(rownum, Column.Action.index)
            action_to_check = action_index.data(Qt.EditRole)
            path_to_check = path_index.data(Qt.EditRole)
            path_to_check_parent = path_to_check.parent
            #   check that rows with the same folder have chosen action
            if path_to_check_parent == row_path_parent:
                assert action_to_check == action
            #   check that rows with another folder don't have chosen action
            else:
                assert action_to_check != action

    @pytest.mark.parametrize("row, key", [
        (0, Qt.Key_D),
        (-1, Qt.Key_D)])
    def test_files_are_deleted(self, main_window_displayed, row, key, qtbot):
        # GIVEN main window displayed
        # WHEN action assigned to files
        self.mark_rows_with_keys([row], [key])
        # QTest.keyPress(self.ui, key, Qt.NoModifier, 100)
        # QTest.keyRelease(self.ui, key)
        data = list()
        for i in range(7):
            index = self.ui.model.createIndex(row, i)
            data.append(index.data(Qt.DisplayRole))
        assert data[Column.Processed.index] is False
        # AND click Execute Action button
        # Watch for the app.worker.finished signal, then start the worker.
        with qtbot.waitSignal(self.ui.files_processor_worker.finished, timeout=10000) as blocker:
            # blocker.connect(self.ui.files_processor_worker.failed)  # Can add other signals to blocker
            QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)
            # app.worker.start()
            # Test will block at this point until signal is emitted or
            # 10 seconds has elapsed
        # QTest.mouseClick(self.ui.pushButton_2, Qt.LeftButton)
        # qtbot.waitSignal(self.ui.files_processor_worker.finished, 10000)
        # THEN files are moved to recycle bin
        data.clear()
        for i in range(7):
            index = self.ui.model.createIndex(row, i)
            data.append(index.data(Qt.DisplayRole))
        print(self.ui.model._data)
        assert data[Column.Processed.index] is True
        file_exists = pathlib.Path(data[Column.Path.index]).is_file()
        assert not file_exists
