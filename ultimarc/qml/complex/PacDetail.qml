import QtQuick 2.4
import QtQuick.Controls 2.15 as QQC2
import QtQuick.Layouts 1.12

import "../simple"

Item {
    id: root

    QQC2.Label {
        id: referenceLabel
        visible: false
        opacity: 0
        width: 30
    }

    ColumnLayout {
        anchors.fill: parent

        Rectangle {
            width: parent.width
            height: childrenRect.height + _units.small_spacing

            color: 'transparent'
            border.color: Qt.darker(palette.window, 1.2)
            border.width: 2

            RowLayout {
                ColumnLayout {
                    QQC2.Label {
                        id: selectedName
                        Layout.alignment: Qt.AlignHCenter
                        font.pointSize: referenceLabel.font.pointSize + 1
                        font.bold: true
                        text: qsTr('Pin Name')
                    }

                    RowLayout {
                        spacing: _units.large_spacing
                        QQC2.Label {
                            leftPadding: _units.small_spacing - 2
                            font.pointSize: referenceLabel.font.pointSize - 1
                            text: "Debounce:"
                        }
                        QQC2.ComboBox {
                            implicitWidth: 87
                            implicitHeight: 26
                            model: ['standard', 'none', 'short', 'long']
                            Component.onCompleted: {
                                currentIndex = find(_devices.device.debounce)
                            }
                            onActivated: {
                                _devices.device.debounce = textAt(currentIndex)
                            }
                        }
                    }
                }

                ColumnLayout {
                    Layout.alignment: Qt.AlignTop
                    RowLayout {
                        QQC2.CheckBox {
                            id: selectedShift
                            font.pointSize: referenceLabel.font.pointSize - 1
                            text: qsTr("Shift")
                        }
                        QQC2.Label {
                            color: "blue"
                            font.pointSize: referenceLabel.font.pointSize - 1
                            text: "Primary Action:"
                        }
                        QQC2.ComboBox {
                            id: selectedAction
                            implicitWidth: 130
                            model: _devices.device.actions
                            onCurrentIndexChanged: {
                                if(activeFocus) {
                                    model.action = selectedAction.textAt(currentIndex)
                                }
                            }
                        }
                        QQC2.Label {
                            color: "red"
                            font.pointSize: referenceLabel.font.pointSize - 1
                            text: "Alternative Action:"
                        }
                        QQC2.ComboBox {
                            id: selectedAltAction
                            implicitWidth: 130
                            model: _devices.device.alt_actions
                            onCurrentIndexChanged: {
                                if (activeFocus) {
                                    model.action = selectedAltAction.textAt(currentIndex)
                                }
                            }
                        }
                    }
                    RowLayout {
                        QQC2.CheckBox {
                            id: paclink
                            font.pointSize: referenceLabel.font.pointSize - 1
                            text: qsTr("PacLink")

                            onToggled: {
                                _devices.device.paclink = checked
                            }
                            Component.onCompleted: {
                                checked = _devices.device.paclink
                            }
                        }
                        QQC2.Button {
                            text: {
                                "Macros"
                            }
                            highlighted: true
                            function macroAction () {
                                macrosPopup.open()
                            }
                            onClicked: {
                                macroAction()
                            }
                            Keys.onSpacePressed: macroAction()
                        }

                        MacroPopup {
                            id: macrosPopup
                            onClosed: {
                                _devices.device.update_macro
                            }
                        }
                    }
                }
            }
        }

        GridView {
            id: grid
            y: _units.grid_unit
            implicitWidth: parent.width
            implicitHeight: mainWindow.height - _units.grid_unit

            clip: true
            interactive: false

            cellWidth: 100
            cellHeight: 42

            model: _devices.device_model.details_model
            delegate: Rectangle {
                width: grid.cellWidth
                height: grid.cellHeight

                color: {
                    detailMouse.containsPress ? Qt.darker(palette.button, 1.2) : palette.window
                }
                border {
                    color: Qt.darker(palette.window, 1.2)
                    width: 1
                }
                MouseArea {
                    id: detailMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    function mouseAction() {
                        grid.currentIndex = index
                        // Make sure the grid has the focus again
                        grid.focus = true

                        selectedName.text = model.name
                        selectedShift.checked = model.shift
                        selectedAction.currentIndex = selectedAction.find(model.action, Qt.MatchFixedString)
                        selectedAltAction.currentIndex = selectedAltAction.find(model.alt_action, Qt.MatchFixedString)
                    }
                    onClicked: {
                        mouseAction()
                    }
                    // Not the best way to do this, but it gets the job done.  Setting the first pin
                    // as the selected pin
                    Component.onCompleted: {
                        if (index == 0) {
                            mouseAction()
                        }
                    }
                }
                ColumnLayout {
                    spacing: 1
                    RowLayout {
                        Layout.fillHeight: true
                        Layout.fillWidth: true
                        QQC2.Label {
                            id: pinName
                            leftPadding: 3
                            font.pointSize: referenceLabel.font.pointSize + 1
                            font.bold: true
                            text: qsTr(model.name)
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        QQC2.Label {
                            id: shift
                            text: qsTr("Shift")
                            font.pointSize: referenceLabel.font.pointSize - 1
                            rightPadding: 5
                            font.bold: { model.shift }

                            Connections {
                                target: selectedShift
                                function onCheckedChanged() {
                                    if (grid.currentIndex == index && selectedShift.activeFocus) {
                                        model.shift = selectedShift.checked
                                    }
                                }
                            }
                        }
                    }
                    Rectangle {
                        Layout.preferredWidth: 98
                        height: childrenRect.height
                        Layout.margins: 1

                        RowLayout {
                            spacing: 0

                            Rectangle {
                                width: childrenRect.width
                                height: childrenRect.height
                                color: "transparent"

                                QQC2.Label {
                                    id: action
                                    color: "blue"
                                    bottomPadding: 1
                                    leftPadding: 1
                                    width: 49
                                    font.pointSize: referenceLabel.font.pointSize
                                    text: model.action
                                    font.bold: true
                                    elide: Text.ElideRight

                                    Connections {
                                        target: selectedAction
                                        function onCurrentIndexChanged() {
                                            if (grid.currentIndex == index && selectedAction.activeFocus) {
                                                model.action = selectedAction.textAt(selectedAction.currentIndex)
                                            }
                                        }
                                    }
                                }
                            }

                            Rectangle {
                                width: childrenRect.width
                                height: childrenRect.height
                                color: "transparent"

                                QQC2.Label {
                                    id: altAction
                                    color: "red"
                                    bottomPadding: 1
                                    leftPadding: 3
                                    width: 49
                                    font.pointSize: referenceLabel.font.pointSize
                                    text: model.alt_action
                                    font.bold: true
                                    elide: Text.ElideRight

                                    Connections {
                                        target: selectedAltAction
                                        function onCurrentIndexChanged() {
                                            if (grid.currentIndex == index && selectedAltAction.activeFocus) {
                                                model.alt_action = selectedAltAction.textAt(selectedAltAction.currentIndex)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}