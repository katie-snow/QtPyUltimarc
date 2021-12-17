import QtQuick 2.4
import QtQuick.Controls 2.5 as QQC2
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1

import "../simple"
import "../complex"
import "../dialogs"

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

    FileDialog {
        id: loadFileDialog
    }
    Connections {
        target: loadFileDialog
        function onAccepted() {
            model.load_location = loadFileDialog.file
            //console.log(loadFileDialog.file)
        }
    }

    FileDialog {
        id: saveFileDialog
    }
    Connections {
        target: saveFileDialog
        function onAccepted() {
            model.save_location = saveFileDialog.file
            //console.log(saveFileDialog.file)
        }
    }


    function toMainScreen() {
        canGoBack = false
        detailLoader.source = ''
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
                    "Load File"
                }
                highlighted: true
                onClicked: {
                    loadFileDialog.fileMode = FileDialog.OpenFile
                    loadFileDialog.open()
                }
            }
            QQC2.Button {
                text: {
                    "Write Device"
                }
                highlighted: true
                visible: model.attached
                onClicked: model.write_device
            }
            QQC2.Button {
                text: {
                    "Write File"
                }
                highlighted: true
                onClicked: {
                    saveFileDialog.fileMode = FileDialog.SaveFile
                    saveFileDialog.open()
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
        Loader {
            id: detailLoader
            Layout.fillWidth: true
            Layout.fillHeight: true
            source: model.qml
       }
    }
}