
import QtQuick
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Layouts
import QtQml

import "views"

Window {
    id: mainWindow
    visible: true
    minimumWidth: 800
    minimumHeight: 580
    title: "Ultimarc Editor"
    color: palette.window

    Component.onCompleted: {
        width = 860
        height = 480
    }

    property alias mainList_currentIndex: contentList.currentIndex
    property real margin: 50 + (width - 800) / 4

    Rectangle {
        id: mainWindowContainer
        anchors {
            fill: parent
            leftMargin: margin
            rightMargin: margin
            bottomMargin: margin
        }
        color: "transparent"
        clip: true

        ButtonGroup {
            id: btnGrp
        }

        ColumnLayout {
            anchors {
                fill: parent
            }

            ListView {
                id: contentList

                Layout.preferredWidth: parent.width
                Layout.preferredHeight: parent.height - margin

                model: ["views/DeviceList.qml", "views/DeviceDetails.qml"]
                orientation: ListView.Horizontal
                snapMode: ListView.SnapToItem
                highlightFollowsCurrentItem: true
                highlightRangeMode: ListView.StrictlyEnforceRange
                interactive: false
                highlightMoveVelocity: 3 * contentList.width
                highlightResizeDuration: 0
                cacheBuffer: 2*width
                delegate: Item {
                    id: contentComponent
                    width: contentList.width
                    height: contentList.height
                    Loader {
                        id: contentLoader
                        source: contentList.model[index]
                        anchors.fill: parent
                    }
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignBottom
                Layout.maximumHeight: activateButton.height
                Button {
                    text: "About"
                    Layout.alignment: Qt.AlignLeft
                }
                Item {
                    Layout.fillWidth: true
                }
                Button {
                    id: activateButton
                    text: "Next"

                    Component.onCompleted: {
                        if (btnGrp.checkState === Qt.Unchecked) {
                            enabled = false
                        }
                    }

                    Connections {
                        target: btnGrp
                        function onClicked(button) {
                            activateButton.enabled = true
                        }
                    }

                    onClicked: activate ()


                    function activate () {
                        if (contentList.currentIndex === 0) {
                            activateButton.text = "Prev"
                            contentList.currentIndex++
                        }
                        else {
                            activateButton.text = "Next"
                            contentList.currentIndex = -1
                            contentList.currentIndex = 0

                            // Currently this allows the Loader qml to work correctly.  Leaving the button selected and
                            // entering the detail page will not reload the Loader if the user does not click on the
                            // radio button again
                            btnGrp.checkState = Qt.Unchecked
                            enabled = false
                        }
                    }
                }
            }
        }
    }
}
