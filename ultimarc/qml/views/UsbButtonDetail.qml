import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "../complex"

Item {
    id: root

    Label {
        id: referenceLabel
        visible: false
        opacity: 0
        width: 30
    }

    Rectangle {
        id: keySequenceRect
        anchors {
            top: root.top
            horizontalCenter: parent.horizontalCenter
        }
        width: childrenRect.width
        height: childrenRect.height

        RadioButton {
            id: primaryBtn

            anchors {
                top: parent.top
                left: parent.left
            }
            text: 'Primary Keys'
            font.pointSize: 12

            checked: true
            onToggled: {
                keyStack.replace(priKey)
            }
        }
        RadioButton {
            id: secondaryBtn

            anchors {
                top: parent.top
                left: primaryBtn.right
            }
            text: 'Secondary Keys'
            font.pointSize: 12

            onToggled: {
                keyStack.replace(secKey)
            }
        }
    }

    StackView {
        id: keyStack
        initialItem: priKey
        anchors {
            top: keySequenceRect.bottom
            left: root.left
            right: root.right
            leftMargin: 5
        }

        height: 125
    }

    KeySequence {
        id: priKey

        myModel: _device_model.device.primary_key_sequence
        model: myModel
    }

    KeySequence {
        id: secKey

        myModel: _device_model.device.secondary_key_sequence
        model: myModel
    }

    Rectangle {
        id: actionRect

        anchors {
            top: keyStack.bottom
            left: root.left
            topMargin: 5
        }

        width: childrenRect.width
        height: childrenRect.height

        Label {
            id: actionLabel
            anchors {
                top: parent.top
                left: parent.left
            }
            text: "Action"
            font.pointSize: 13
        }

        RadioButton {
            id: extended

            anchors {
                top: actionLabel.bottom
                left: parent.left
                leftMargin: 15
            }
            text: 'Extended: Send both sequences on every press'
            font.pointSize: 12

            checked: true
            onToggled: {

            }
        }
        RadioButton {
            id: alternate

            anchors {
                top: extended.bottom
                left: parent.left
                leftMargin: 15
            }
            text: 'Alternate: Send primary then secondary on alternate presses'
            font.pointSize: 12

            onToggled: {

            }
        }
        RadioButton {
            id: both

            anchors {
                top: alternate.bottom
                left: parent.left
                leftMargin: 15
            }
            text: 'Both: Send primary on short press, secondary on long press'
            font.pointSize: 12

            onToggled: {

            }
        }
    }

    Rectangle {
        id: ledRect
        anchors {
            top: actionRect.bottom
            left: parent.left
        }

        width: childrenRect.width
        height: childrenRect.height

        Label {
            id: ledLabel
            anchors {
                top: parent.top
                left: parent.left
                topMargin: 15
            }
            text: "LED"
            font.pointSize: 13
        }

        Rectangle {
            id: colorRect
            anchors {
                top: ledLabel.bottom
                left: parent.left
                topMargin: 10
                leftMargin: 30
            }
            border {
                width: 2
            }

            width: 50
            height: 50

            color: Qt.rgba(red, green, blue, 1)

            property real red: redSlider.value.toFixed(2)
            property real green: greenSlider.value.toFixed(2)
            property real blue: blueSlider.value.toFixed(2)
        }

        SliderGroup {
            id: redSlider
            anchors {
                top: ledLabel.bottom
                left: colorRect.right
                leftMargin: 30
            }
            text: 'Red'
        }

        SliderGroup {
            id: greenSlider
            anchors {
                top: redSlider.bottom
                left: colorRect.right
                topMargin: 10
                leftMargin: 30
            }
            text: 'Green'
        }

        SliderGroup {
            id: blueSlider
            anchors {
                top: greenSlider.bottom
                left: colorRect.right
                topMargin: 10
                leftMargin: 30
            }
            text: 'Blue'
        }
    }
}