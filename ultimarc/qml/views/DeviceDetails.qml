import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../complex"
import "../dialogs"

Item {
    id: deviceDetails

   ListView {
        id: detailList
        anchors.fill: parent
        clip: true
        model: _devices.selected_device

        delegate:
            Item {
                anchors.fill: parent

                Label {
                    id: deviceClass
                    anchors {
                        top: parent.top
                        left: parent.left
                    }
                    font.pointSize: 20
                    text: model.device_class_descr
                    //text: model.qml
                }

                Label {
                    id: deviceName
                    anchors {
                        top: deviceClass.bottom
                        left: parent.left
                    }
                    font.pointSize: 16
                    text: model.device_name
                    opacity: 0.6
               }

                Label {
                    id: deviceKey
                    anchors {
                        top: deviceClass.bottom
                        left: deviceName.right
                        leftMargin: 5
                        topMargin: 6
                    }
                    font.pointSize: 11
                    text: model.device_key
                    opacity: 0.6
               }

               Button {
                    id: deviceWriteFile
                    anchors {
                        top: parent.top
                        right: parent.right
                        topMargin: 5
                    }
                    text: "Write File"
                    highlighted: true
                    onClicked: {
                        saveFileDialog.fileMode = FileDialog.SaveFile
                        saveFileDialog.open()
                    }
               }

               Button {
                    id: deviceWrite
                    anchors {
                        top: parent.top
                        right: deviceLoadFile.left
                        topMargin: 5
                        rightMargin: 10
                    }
                    text: "Format Device"

                    highlighted: model.attached
                    enabled: model.attached
                    onClicked: model.write_device
               }

               Button {
                    id: deviceLoadFile
                    anchors {
                        top: parent.top
                        right: deviceWriteFile.left
                        topMargin: 5
                        rightMargin: 10
                    }
                    text: "Load File"
                    highlighted: true
                    onClicked: {
                        loadFileDialog.fileMode = FileDialog.OpenFile
                        loadFileDialog.open()
                    }
                }

                Loader {
                    id: detailLoader
                    anchors {
                        top: deviceName.bottom
                        left: parent.left
                        right: parent.right
                        bottom: parent.bottom
                    }
                    source: model.qml
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
            }
    }
}