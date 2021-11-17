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
            height: childrenRect.height

            color: 'transparent'
            border.color: Qt.darker(palette.window, 1.2)
            border.width: 2

            RowLayout {
                spacing: _units.large_spacing
                anchors.right: parent.right
                QQC2.Label {
                    id: selectedName
                    leftPadding: _units.grid_unit
                    font.pointSize: referenceLabel.font.pointSize + 1
                    font.bold: true
                    text: qsTr('Pin Name')
                }

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
                    model: _actions
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
                    model: _alt_actions
                    onCurrentIndexChanged: {
                        if (activeFocus) {
                            model.action = selectedAltAction.textAt(currentIndex)
                        }
                    }
                }
            }
        }

        GridView {
            id: grid
            y: _units.grid_unit
            width: parent.width
            height: mainWindow.height - _units.grid_unit

            clip: true
            interactive: false

            cellWidth: 100
            cellHeight: 43

            model: _d.device_details
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
                        selectedAction.currentIndex = selectedAction.find(model.action)
                        selectedAltAction.currentIndex = selectedAltAction.find(model.alt_action)
                    }
                    onClicked: {
                        mouseAction()
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
                        Layout.preferredWidth: 100
                        height: childrenRect.height
                        Layout.margins: 2

                        RowLayout {
                            Layout.fillWidth: true

                            QQC2.Label {
                                id: action
                                color: "blue"
                                Layout.fillWidth: true
                                bottomPadding: 3
                                leftPadding: 3
                                font.pointSize: referenceLabel.font.pointSize
                                text: model.action
                                font.bold: true

                                Connections {
                                    target: selectedAction
                                    function onCurrentIndexChanged() {
                                        if (grid.currentIndex == index && selectedAction.activeFocus) {
                                            model.action = selectedAction.textAt(selectedAction.currentIndex)
                                        }
                                    }
                                }
                            }
                            Item {
                                Layout.fillWidth: true
                            }
                            QQC2.Label {
                                id: altAction
                                color: "red"
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignRight
                                bottomPadding: 3
                                rightPadding: 3
                                font.pointSize: referenceLabel.font.pointSize
                                text: model.alt_action
                                font.bold: true

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