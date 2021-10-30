import QtQuick 2.4
import QtQuick.Controls 2.5 as QQC2
import QtQuick.Layouts 1.15

import "../simple"
import "../complex"

Item {
    id: deviceDelegate
    anchors.fill: parent

    signal stepForward
    property bool focused: contentList.currentIndex === 1
    enabled: focused

    QQC2.Label {
        id: referenceLabel
        visible: false
        opacity: 0
    }

    function toMainScreen() {
        canGoBack = false
        contentList.currentIndex--
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.BackButton
        onClicked:
            if (mouse.button == Qt.BackButton)
                toMainScreen()
    }

    ColumnLayout {
        x: mainWindow.margin
        y: _units.grid_unit
        width: parent.width - mainWindow.margin
        spacing: _units.large_spacing * 3
        RowLayout {
            id: tools
            Layout.fillWidth: true
            spacing: _units.large_spacing * 3

            QQC2.Button {
                id: backButton
                icon.name: "qrc:/icons/go-previous"
                text: qsTr("Back")
                onClicked: toMainScreen()
            }
            Item {
                Layout.fillWidth: true
            }
            QQC2.Button {
                text: {
                    "Write to..."
                }
                highlighted: true

                onClicked:
                {
                    // Not Working
                    if (writeBoardDialog.visible)
                        return
                    if (model.attached)
                        writeBoardDialog.visible = true
                    else
                        fileDialog.open()
                }
            }
        }
        RowLayout {
            spacing: _units.large_spacing
            Item {
                Layout.preferredWidth: Math.round(_units.grid_unit * 3.5) + _units.grid_unit
                Layout.preferredHeight: Math.round(_units.grid_unit * 3.5)
                Layout.alignment: Qt.AlignHCenter

                IndicatedImage {
                    anchors.fill: parent
                    x: _units.grid_unit
                    source: model.icon
                    fillMode: Image.PreserveAspectFit
                    sourceSize.width: parent.width
                    sourceSize.height: parent.height
                }
            }
            ColumnLayout {
                Layout.fillHeight: true
                spacing: _units.large_spacing
                RowLayout {
                    Layout.fillWidth: true
                    QQC2.Label {
                        Layout.fillWidth: true
                        font.pointSize: referenceLabel.font.pointSize + 4
                        text: model.device_class_descr
                    }
                    QQC2.Label {
                        font.pointSize: referenceLabel.font.pointSize + 2
                        visible: model.attached
                        text: model.device_name
                        opacity: 0.6
                    }
                }
                ColumnLayout {
                    width: parent.width
                    spacing: _units.large_spacing
                    QQC2.Label {
                        font.pointSize: referenceLabel.font.pointSize + 1
                        visible: model.attached
                        text: model.device_key
                        opacity: 0.6
                    }
                    QQC2.Label {
                        font.pointSize: referenceLabel.font.pointSize - 1
                        text: model.description
                        opacity: 0.6
                    }
                }
            }
        }

        Rectangle {
            color: "transparent"
            border.color: "gray"
            border.width: 2
            width: childrenRect.width + _units.large_spacing
            height: childrenRect.height
            RowLayout {
                spacing: _units.large_spacing

                QQC2.Label {
                    leftPadding: _units.grid_unit
                    font.pointSize: referenceLabel.font.pointSize + 1
                    text: "Selected Pin"
                }
                QQC2.CheckBox {
                    font.pointSize: referenceLabel.font.pointSize - 1
                    text: qsTr("Shift")
                }
                QQC2.Label {
                    color: "blue"
                    font.pointSize: referenceLabel.font.pointSize - 1
                    text: "Primary Action:"
                }
                QQC2.ComboBox {
                    implicitWidth: 75
                    model: ["A", "B", "C", "D"]
                }
                QQC2.Label {
                    color: "red"
                    font.pointSize: referenceLabel.font.pointSize - 1
                    text: "Alternative Action:"
                }
                QQC2.ComboBox {
                    implicitWidth: 75
                    model: ["A", "B", "C", "D"]
                }
            }
        }
        Grid {
            x: mainWindow.margin
            y: _units.grid_unit - 3
            columns: 6
            spacing: _units.small_spacing
            flow: Grid.TopToBottom

            Component {
                id: deviceDetailsComponent

                Rectangle {
                        color: "transparent"
                        border.color: "gray"
                        border.width: 1

                        width: childrenRect.width
                        height: childrenRect.height
                        ColumnLayout {
                            spacing: 1
                            RowLayout {
                                Layout.fillHeight: true
                                Layout.fillWidth: true
                                QQC2.Label {
                                    leftPadding: 3
                                    font.pointSize: referenceLabel.font.pointSize + 1
                                    font.bold: true
                                    text: qsTr(model.name)
                                }

                                QQC2.Label {
                                    text: qsTr("Shift")
                                    font.pointSize: referenceLabel.font.pointSize - 1
                                    font.bold: true
                                }

                            }
                            RowLayout {
                                Layout.fillHeight: true
                                Layout.fillWidth: true
                                QQC2.Label {
                                    color: "blue"
                                    bottomPadding: 3
                                    leftPadding: 3
                                    font.pointSize: referenceLabel.font.pointSize - 1
                                    text: "Shift L"
                                }
                                Item {
                                    Layout.fillWidth: true
                                }
                                QQC2.Label {
                                    color: "red"
                                    bottomPadding: 3
                                    rightPadding: 3
                                    font.pointSize: referenceLabel.font.pointSize - 1
                                    text: "C"
                                }
                            }
                        }
                   }
            }

            Repeater {
                model: _d.device_details
                delegate: deviceDetailsComponent
            }
        }
    }
}