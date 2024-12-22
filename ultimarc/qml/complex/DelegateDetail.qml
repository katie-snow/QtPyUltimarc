import QtQuick 2.4
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.15

import "../complex"
import "../dialogs"

Item {
    id: deviceDelegate
    anchors.fill: parent

    property bool focused: contentList.currentIndex === 1
    property bool cleared: false
    enabled: focused

    Label {
        id: referenceLabel
        visible: false
        opacity: 0
    }

    Connections {
        // Clear loader when leaving the page
        target: contentList
        function onCurrentIndexChanged() {
            if (!focused && !cleared) {
                detailLoader.source = ''
                cleared = true
            }
            else {
                cleared = false
            }
        }
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

    ColumnLayout {
        x: mainWindow.margin - (mainWindow.margin / 2)
        y: _units.grid_unit
        width: parent.width - (mainWindow.margin - (mainWindow.margin / 2))
        spacing: _units.large_spacing * 3
        RowLayout {
            id: tools
            Layout.fillWidth: true
            spacing: _units.large_spacing * 3

            ColumnLayout {
                Layout.fillWidth: true
                spacing: _units.large_spacing

                Label {
                    Layout.fillWidth: true
                    font.pointSize: referenceLabel.font.pointSize + 4
                    text: model.device_class_descr
                }

                RowLayout {
                    width: parent.width
                    spacing: _units.large_spacing

                    Label {
                        font.pointSize: referenceLabel.font.pointSize + 2
                        visible: model.attached
                        text: model.device_name
                        opacity: 0.6
                    }

                    Label {
                        font.pointSize: referenceLabel.font.pointSize
                        text: model.attached ? model.device_key : model.description
                        opacity: 0.6
                    }
                }
            }
            Button {
                text: {
                    "Write Device"
                }
                highlighted: true
                visible: model.attached
                onClicked: model.write_device
            }
            Button {
                text: {
                    "Load File"
                }
                highlighted: true
                onClicked: {
                    loadFileDialog.fileMode = FileDialog.OpenFile
                    loadFileDialog.open()
                }
            }
            Button {
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
        Loader {
            id: detailLoader
            Layout.fillWidth: true
            Layout.fillHeight: true
            source: model.qml
       }
    }
}