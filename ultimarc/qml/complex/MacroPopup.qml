import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../simple"

Popup {
    id: root
    height: 275
    width: 475
    modal: true
    focus: true
    clip: true
    closePolicy: Popup.CloseOnEscape

    ColumnLayout {
        anchors.fill: parent
        spacing: _units.large_spacing * 2
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            RowLayout {
                Label { text: qsTr("Name:") }
                Rectangle {
                    width: Math.round(_units.grid_unit + 100) + _units.small_spacing
                    height: Math.round(_units.grid_unit + _units.small_spacing)

                    color: 'white'
                    border.color: Qt.darker(palette.window, 1.2)
                    border.width: 2
                    TextInput {
                        id: macro_name
                        anchors.fill: parent
                        anchors.leftMargin: 3
                        focus: true
                    }
                }

                Label { text: qsTr("Action:") }
                ComboBox {
                    id: action
                    implicitWidth: 130
                    model: _devices.device.actions
                    onCurrentIndexChanged: {
                        if(activeFocus) {
                            var seperator = ""
                            if (macro_actions.length > 0)
                            {
                                seperator = ", "
                            }
                            macro_actions.text = macro_actions.text + seperator + action.textAt(currentIndex)
                        }
                    }
                }
            }
            RowLayout {
                Label { text: qsTr("Macro Actions:") }
                Rectangle {
                    width: Math.round(_units.grid_unit + 200) + _units.small_spacing
                    height: Math.round(_units.grid_unit + _units.small_spacing)

                    color: 'transparent'
                    border.color: Qt.darker(palette.window, 1.2)
                    border.width: 2
                    TextInput {
                        id: macro_actions
                        anchors.fill: parent
                        anchors.leftMargin: 3
                        focus: true
                    }
                }
            }
        }

        RowLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true

                color: 'transparent'
                border.color: Qt.darker(palette.window, 1.2)
                border.width: 2
                ListView {
                    id: list
                    anchors.fill: parent
                    focus: true
                    clip: true

                    highlight: Rectangle { color: "lightsteelblue"; radius: 5 }

                    header: RowLayout {
                        width: parent.width
                        height: childrenRect.height

                        spacing: 0
                        Rectangle {
                            implicitWidth: Math.round(parent.width / 3)
                            implicitHeight: Math.round(_units.grid_unit)

                            border.color: Qt.darker(palette.window, 1.2)
                            border.width: 1

                            Text { text: "<b>Name</b>" }
                        }
                        Rectangle {
                            implicitWidth: Math.round(parent.width * 2 / 3)
                            implicitHeight: Math.round(_units.grid_unit)

                            border.color: Qt.darker(palette.window, 1.2)
                            border.width: 1

                            Text { text: "<b>Action</b>" }
                        }
                    }

                    model: _devices.device.macros
                    delegate: Item {
                        id: macroRow
                        activeFocusOnTab: true
                        width: Math.round(list.width)
                        height: Math.round(_units.grid_unit)
                        RowLayout {
                            spacing: 0
                            anchors.fill: parent
                            Rectangle {
                                implicitWidth: Math.round(parent.width / 3)
                                implicitHeight: Math.round(_units.grid_unit)

                                color: 'transparent'
                                border.color: Qt.darker(palette.window, 1.2)
                                border.width: 1

                                Text {
                                    id: macroName
                                    text: name
                                }
                            }
                            Rectangle {
                                implicitWidth: Math.round(parent.width * 2 / 3)
                                implicitHeight: Math.round(_units.grid_unit)

                                color: 'transparent'
                                border.color: Qt.darker(palette.window, 1.2)
                                border.width: 1

                                Text {
                                    id: macroActions
                                    text: action
                                }
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                list.currentIndex = index
                            }
                        }
                        Connections {
                            target: macroEdit
                            function onReleased() {
                                if (macroRow.ListView.isCurrentItem) {
                                    if (macroEdit.text == 'Edit') {
                                        macro_name.text = macroName.text
                                        macro_actions.text = macroActions.text
                                        macroEdit.text = 'Done'
                                   }
                                   else {
                                        model.name = macro_name.text
                                        model.action = macro_actions.text
                                        macroEdit.text = 'Edit'
                                   }
                                }
                            }
                        }
                    }
                }
            }
            ColumnLayout {
                Layout.alignment: Qt. AlignTop
                ColumnLayout {
                    Layout.alignment: Qt.AlignRight
                    Button {
                        text: "Add"
                        highlighted: true
                        onClicked: {
                            macroEdit.text = 'Edit'
                            _devices.device.macros.add_macro = macro_name.text + ':' + macro_actions.text
                        }
                    }
                    Button {
                        id: macroEdit
                        text: "Edit"
                        highlighted: true
                    }
                    Button {
                        id: macroRemove
                        text: "Remove"
                        highlighted: true
                        onClicked: {
                            macroEdit.text = 'Edit'
                            _devices.device.macros.remove_macro = list.currentIndex
                        }
                    }
                    Item {
                        Layout.fillHeight: true
                    }
                    Button {
                        Layout.alignment: Qt.AlignBottom
                        text: "Close"
                        highlighted: true
                        onClicked: {
                            macro_name.text = ""
                            macro_actions.text = ""
                            root.close()
                        }
                    }
                }
            }
        }
    }
}