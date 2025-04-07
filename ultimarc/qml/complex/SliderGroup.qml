import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    property alias text: sliderLabel.text
    property alias value: slider.value

    height: childrenRect.height
    width: childrenRect.width

    Label {
        id: sliderLabel
        anchors {
            top: root.top
        }
    }

    Slider {
        id: slider
        anchors {
            top: root.top
            left: sliderLabel.right
            leftMargin: 60 - sliderLabel.width
        }
        implicitWidth: 400

        from: 0
        to: 1
        value: 1
    }
}