import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property alias gridModel: keySequenceGrid.model

    height: childrenRect.height
    width: childrenRect.width

    Component.onCompleted: {
        console.log(keySequenceGrid.count)
        console.log(keySequenceGrid[0])
        console.log (height)
    }

    GridView {
        id: keySequenceGrid

        anchors {
            top: root.top
            left: root.left
            right: root.right
            margins: 2
        }


        clip: true
        interactive: true
        cellWidth: 113
        cellHeight: 26
        //model: _device_model.device.primary_key_sequence
        delegate: Rectangle {
            id: key
            //required property int index

            width: keySequenceGrid.cellWidth
            height: keySequenceGrid.cellHeight

            anchors {
                margins: 2
            }

            border {
                color: Qt.darker(palette.window, 1.2)
                width: 1
            }

            Label {
                id: test
                width: keySequenceGrid.cellWidth
                height: keySequenceGrid.cellHeight

                text: model.action
                //text: 'hi'
            }

            // ComboBox {
            //     id: action
            //     implicitWidth: keySequenceGrid.cellWidth
            //     height: keySequenceGrid.cellHeight
            //
            //     indicator: Canvas {
            //         id: canvas
            //         // Don't paint an indicator on the dropdown
            //     }
            //
            //     model: _device_model.device.action_model
            //
            //     Component.onCompleted: { setKey () }
            //     function setKey () {
            //         //console.log ('setKey: ' + index + ' ' + currentText)
            //         //keySequenceGrid.model.keyIndex = index
            //         //currentIndex = indexOfValue(keySequenceGrid.model.key)
            //     }
            //
            //     onActivated: { selectKey () }
            //     function selectKey () {
            //         console.log ('selectKey: ' + index + ' ' + currentText)
            //         //keySequenceGrid.model.keyIndex = index
            //         keySequenceGrid.model.key = currentText
            //         console.log ('selectKey - Model: ' + keySequenceGrid.model.key)
            //     }
            // }
        }
    }
}