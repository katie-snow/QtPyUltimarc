import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

GridView {
    id: keySequenceGrid

    property var myModel

    anchors {
        margins: 2
    }

    clip: true
    interactive: true
    cellWidth: 113
    cellHeight: 26

    delegate: Rectangle {
        id: key
        required property int index

        width: keySequenceGrid.cellWidth
        height: keySequenceGrid.cellHeight

        anchors {
            margins: 2
        }

        border {
            color: Qt.darker(palette.window, 1.2)
            width: 1
        }

        ComboBox {
            id: action
            implicitWidth: keySequenceGrid.cellWidth
            height: keySequenceGrid.cellHeight

            indicator: Canvas {
                id: canvas
                // Don't paint an indicator on the dropdown
            }

            model: _device_model.device.action_model

            Component.onCompleted: { setKey () }
            function setKey () {
                myModel.keyIndex = index
                currentIndex = indexOfValue(myModel.key)
            }

            onActivated: { selectKey () }
            function selectKey () {
                myModel.keyIndex = index
                myModel.key = currentText
            }
        }
    }
}