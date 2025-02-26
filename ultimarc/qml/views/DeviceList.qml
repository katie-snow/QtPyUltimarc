import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: devicesList

    property string activate_str: 'devicesList'

    GridView {
        id: gridView
        anchors {
            top: parent.top
            bottom: parent.bottom
            left: parent.left
            right: parent.right
            leftMargin: 80
            topMargin: 80

            // Adjust this number to keep empty configuration on one side of the grid
            bottomMargin: 200
        }

        model: _sort_devices

        cellWidth: 200
        cellHeight: 30

        flow: GridView.FlowTopToBottom
        clip: true

        interactive: false
        keyNavigationEnabled: true
        keyNavigationWraps: true
        focus: true

        highlight: Rectangle {
            color: 'light gray'
            width: gridView.cellWidth
        }

        delegate: Component {
            RadioButton {
                property GridView __gv: GridView.view
                width: gridView.cellWidth
                height: gridView.cellHeight

                // keep
                text: model.device_name
                contentItem: Text {
                    text: model.device_name
                    font.pointSize: 14
                    leftPadding: parent.indicator.width + parent.spacing + 4
                    verticalAlignment: Text.AlignVCenter
                }

                Component.onCompleted: {
                    if (index === 0) {
                        checked = true
                        moveCurrentIndex()
                    }
                }

                onClicked: moveCurrentIndex ()

                function moveCurrentIndex () {
                    __gv.currentIndex = model.index

                    // This sets the currently selected device in the underlying model
                    // Allows DeviceDetails to get the correct model later
                    model.selected_device = model.index
                }

                Keys.onReleased: {
                    checked = true
                    moveCurrentIndex()
                }
            }
        }
    }
}
