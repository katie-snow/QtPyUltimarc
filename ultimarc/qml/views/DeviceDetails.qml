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
        interactive: false
        focus:true

        model: _devices.selected_device
        delegate:
            Item {
                width: detailList.width
                height: detailList.height

                Label {
                    id: deviceName
                    anchors {
                        top: parent.top
                        left: parent.left
                    }
                    font.pointSize: 20
                    text: model.device_name
                }

                Label {
                    id: deviceKey
                    anchors {
                        top: deviceName.bottom
                        left: parent.left
                        leftMargin: 5
                        topMargin: 6
                    }
                    font.pointSize: 13
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
                    text: "Save"
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

                    property int result

                    contentItem: Text {
                        text: 'Format Device'
                        color: model.attached ? 'black' : Qt.darker(palette.window, 1.2)
                    }

                    highlighted: model.attached
                    enabled: model.attached
                    onClicked: {
                        result = model.write_device
                        //console.log(result)
                        if (result == 1) {
                            deviceWritePopup.result = 'Write Complete'
                        }
                        else {
                            deviceWritePopup.result = 'Write Failed'
                        }
                        deviceWritePopup.open()
                    }
               }

               Button {
                    id: deviceLoadFile
                    anchors {
                        top: parent.top
                        right: deviceWriteFile.left
                        topMargin: 5
                        rightMargin: 10
                    }
                    text: "Load"
                    highlighted: true
                    onClicked: {
                        loadFileDialog.fileMode = FileDialog.OpenFile
                        loadFileDialog.open()
                    }
                }

                Rectangle {
                    anchors {
                            top: deviceKey.bottom
                            left: parent.left
                            right: parent.right
                            bottom: parent.bottom
                    }
                    color: "transparent"

                    Loader {
                        id: detailLoader

                        Component.onCompleted: {
                                detailLoader.setSource (model.qml, {"width": parent.width, "height": parent.height})

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

                Timer {
                    id: timeout
                    interval: 1500
                    running: true
                    repeat: false

                    onTriggered: deviceWritePopup.close()
                }

                Popup {
                    id: deviceWritePopup
                    height: 100
                    width: 200
                    modal: true
                    focus: true
                    clip: true
                    closePolicy: Popup.CloseOnEscape

                    anchors.centerIn: parent

                    property alias result: title.text

                    onOpened: timeout.restart()
                    Rectangle {
                        anchors.fill: parent
                        color:  'lavender'

                        Label {
                            id: title
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 20
                            text: 'Something is happening'
                            font.pointSize: 12
                        }

                        Button {
                            anchors {
                                top: title.bottom
                                horizontalCenter: title.horizontalCenter
                                topMargin: 10
                            }
                            text: "Close"
                            highlighted: true
                            onClicked: {
                                deviceWritePopup.close()
                            }
                        }
                    }
                }
            }
    }
}