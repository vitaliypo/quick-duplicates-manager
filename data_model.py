import os
import pathlib
import re
from collections import namedtuple
from enum import Enum

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox


class File:
    def __init__(self, path, size, modified_date, modified_time, group):
        self.action = Action.none
        self.processed = False
        self.group = group
        self.modified_time = modified_time
        self.modified_date = modified_date
        self.size = size
        self.path = pathlib.Path(path)

    def set_action(self, action):
        self.action = action
        pass


class CloneSpyResultsReader:
    def __init__(self, path):
        results = self.get_results_from_file(path)
        self.duplicates = self.create_Files_from_results(results)

    def create_Files_from_results(self, results):
        files = list()
        for result in results:
            file = File(result[3], result[0], result[1], result[2], result[4])
            files.append(file)
        return files

    def get_results_from_file(self, path):
        results = pathlib.Path(path).read_text().strip()
        # print(results)
        results_list = list(results.splitlines())
        results_parsed_list = list()
        group_number = 1
        for line in results_list:
            # todo add handling of two spaces at path
            chunks = re.split("\s{2}", line)
            filtered_chunks = list()
            for chunk in chunks:
                if len(chunk) != 0 and chunk != ' ' and chunk != '':
                    filtered_chunks.append(chunk)
            if len(filtered_chunks) <= 1:
                group_number += 1
            if len(filtered_chunks) > 1:
                if len(filtered_chunks) != 4:
                    print(filtered_chunks)  # print non-typical chunks for debugging purpose
                filtered_chunks.append(group_number)
                results_parsed_list.append(filtered_chunks)
        return results_parsed_list

    def reformat_data_to_model(self):
        rows = list()
        for file in self.duplicates:
            row = [
                file.group,
                file.path,
                file.modified_date,
                file.modified_time,
                file.size,
                file.action,
                file.processed
            ]
            rows.append(row)
        return rows


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, current_errors_list):
        super(TableModel, self).__init__()
        self._data = data
        self.current_errors = current_errors_list

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return [element.string_representation for element in Column][section]
        return QtCore.QVariant()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            value = self._data[index.row()][index.column()]
            if isinstance(value, pathlib.Path):
                return str(value)
            return value
        if role == Qt.BackgroundRole:
            value = self._data[index.row()][0]
            if value % 2 != 0:
                return QtGui.QColor(220, 255, 220)
        if role == Qt.ForegroundRole:
            value = self._data[index.row()][-1]
            if value:  # to set grey color for processed rows
                return QtGui.QColor("grey")
            else:  # To set red color for rows which cause errors
                for error in self.current_errors:
                    if error.row_causing_the_error == index.row():
                        return QtGui.QColor("red")
                # return QtGui.QColor("black")

        if role == Qt.EditRole:
            value = self._data[index.row()][index.column()]
            return value

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            column = index.column()
            self._data[row][column] = value

            # Here we need to emit dataChanged signal for all rows of group \
            # to update row colors depending on errors of group
            current_group_index = self.createIndex(index.row(), Column.Group.index)
            current_group = current_group_index.data(Qt.DisplayRole)
            group_indexes = self.find_indexes_of_value(Column.Group.index, current_group)
            group_indexes.sort(key=lambda element: element.row())
            first_index_of_group = group_indexes[0]
            last_index_of_group = self.createIndex(group_indexes[-1].row(), Column.Processed.index)

            self.dataChanged.emit(first_index_of_group, last_index_of_group)

            return True
        return QtCore.QAbstractTableModel.setData(self, index, value, role)

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def find_hardlinks_and_source_in_group(self, group):
        indexes_of_group = self.find_indexes_of_value(Column.Group.value, group)
        indexes_of_hardlink_in_group = list()
        index_of_source_for_hardlink_in_group = None
        for index in indexes_of_group:
            action_index = self.createIndex(index.row, Column.Action.value)
            action = action_index.data(Qt.DisplayRole)
            if action == Action.hardlink.value:
                indexes_of_hardlink_in_group.append(action_index)
            elif action == Action.source.value:
                index_of_source_for_hardlink_in_group = action_index
        return indexes_of_hardlink_in_group, index_of_source_for_hardlink_in_group

    def get_amount_of_groups(self):
        last_row_number = self.rowCount(0) - 1
        max_group_number = self.createIndex(last_row_number, Column.Group.index).data(Qt.DisplayRole)
        return max_group_number

    def find_indexes_of_value(self, column, value, start_row=0):
        results = list()
        if column == Column.Group.index:  # assuming rows can't be sorted manually
            for row_number in range(start_row, self.rowCount(0)):
                index = self.createIndex(row_number, column)
                value_from_table = index.data(Qt.DisplayRole)
                if value_from_table == value:
                    results.append(index)
                elif value_from_table > value:
                    break
        else:
            for row_number in range(self.rowCount(0)-1):
                index = self.createIndex(row_number, column)
                value_from_table = index.data(Qt.DisplayRole)
                if value_from_table == value:
                    results.append(index)
        return results


class Column(namedtuple('Column', 'index string_representation'), Enum):
    Group = 0, 'Group'
    Path = 1, 'Path'
    Modified_date = 2, "Modified date"
    Modified_time = 3, "Modified time"
    Size = 4, "Size"
    Action = 5, "Action"
    Processed = 6, "Processed"


class Action(Enum):
    delete = "Delete"
    hardlink = "Hardlink"
    source = "Source for Hardlink"
    none = None


class ValidationErrorType(Enum):
    source_for_hardlink_absence = "Source for hardlink is absent in the group"
    hardlink_absence = "Hardlink is absent in the group"
    more_than_one_source_in_group = "More than one source for hardlink set for group"


class ValidationError:
    def __init__(self, error_type, row_causing_the_error):
        self.error_type = error_type
        self.row_causing_the_error = row_causing_the_error
