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
            cellWidth: 200
            cellHeight: 30
            flow: GridView.FlowTopToBottom
            clip: true
            interactive: false

            model: _sort_devices
            delegate: RadioButton {
                width: gridDeviceList.cellWidth
                height: gridDeviceList.cellHeight

                text: model.device_name
                ButtonGroup.group: btnGrp

                onClicked: {
                    gridDeviceList.currentIndex = index
                    // Make sure the grid has the focus again
                    gridDeviceList.focus = true
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
