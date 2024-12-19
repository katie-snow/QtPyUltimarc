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
        x: mainWindow.margin
        y: _units.grid_unit
        width: parent.width - mainWindow.margin
        spacing: _units.large_spacing * 3
        RowLayout {
            id: tools
            Layout.fillWidth: true
            spacing: _units.large_spacing * 3

            Item {
                Layout.fillWidth: true
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
                    "Write Device"
                }
                highlighted: true
                visible: model.attached
                onClicked: model.write_device
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
                    Label {
                        Layout.fillWidth: true
                        font.pointSize: referenceLabel.font.pointSize + 4
                        text: model.device_class_descr
                    }
                    Label {
                        font.pointSize: referenceLabel.font.pointSize + 2
                        visible: model.attached
                        text: model.device_name
                        opacity: 0.6
                    }
                }
                ColumnLayout {
                    width: parent.width
                    spacing: _units.large_spacing
                    Label {
                        font.pointSize: referenceLabel.font.pointSize + 1
                        visible: model.attached
                        text: model.device_key
                        opacity: 0.6
                    }
                    Label {
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