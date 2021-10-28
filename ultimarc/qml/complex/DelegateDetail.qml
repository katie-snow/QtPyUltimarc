import QtQuick 2.4
import QtQuick.Controls 2.2 as QQC2
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
        Grid {
            Component {
                id: rectangleComponent2

                Rectangle {
                        width: 80; height: 30
                        color: "green"
                        Text { text: model.index + " " + model.name  }
                }
            }
            columns: 3; spacing: 20
            Repeater {
                model: _d.device_details
                delegate: rectangleComponent2
                //Rectangle { width: 20; height: 20; radius: 10; color: "green" }
            }
        }
    }
}