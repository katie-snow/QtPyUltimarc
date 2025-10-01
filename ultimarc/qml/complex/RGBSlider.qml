import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    property string text: 'default'
    property alias sliderWidth: mySlider.width
    property alias value: mySlider.value

    height: childrenRect.height
    width: childrenRect.width

    Label {
        id: myLabel
        anchors {
            top: root.top
        }
        text: root.text
    }

    Slider {
        id: mySlider
        anchors {
            top: root.top
            left: myLabel.right
            leftMargin: 60 - myLabel.width
        }

        from: 0
        to: 1
        value: 1
    }
}