import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "../complex"

Item {
    id: deviceList

    ColumnLayout {
        anchors.fill: parent

        // Image
        Rectangle {
            color: "light blue"
            Layout.fillWidth: true
            Layout.preferredHeight: Math.round(_units.grid_unit * 4.5)
        }

        GridView {
            id: gridDeviceList
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: parent.width / 2 - cellWidth / 2
            // Adjust bottomMargin as empty devices are added to the list
            Layout.bottomMargin: _units.grid_unit * 8
            cellWidth: 200
            cellHeight: 30
            flow: GridView.FlowTopToBottom
            clip: true
            interactive: false
            keyNavigationEnabled: true
            keyNavigationWraps: true
            focus: true

            highlight: Rectangle {
                color: 'transparent'
                width: gridDeviceList.width
            }

            model: _sort_devices
            delegate: RadioButton {
                width: gridDeviceList.cellWidth
                height: gridDeviceList.cellHeight
                clip: true

                text: model.device_name
                ButtonGroup.group: btnGrp

                contentItem: Text {
                    text: parent.text
                    font.pointSize: 14
                    leftPadding: parent.indicator.width + parent.spacing + 4
                    verticalAlignment: Text.AlignVCenter
                }

                Component.onCompleted: {
                    if (index === 0) {
                        checked = true
                        moveCurrentIndex()
                        focus = true
                    }
                }

                onClicked: moveCurrentIndex ()

                function moveCurrentIndex () {
                    gridDeviceList.currentIndex = index
                    // Make sure the grid has the focus again
                    gridDeviceList.focus = true
                }

                Keys.onReleased: {
                    checked = true
                }

                Connections {
                    // Loads the selected device to be displayed on the next page
                    target: activateButton
                    function onClicked(button) {
                        if (gridDeviceList.currentIndex === index) {
                            model.selected_device = gridDeviceList.currentIndex
                            // Reset the currentIndex so the grid doesn't set the selected device when there isn't a
                            // selection anymore
                            gridDeviceList.currentIndex = -1
                        }
                    }
                }
            }
        }
    }
}
