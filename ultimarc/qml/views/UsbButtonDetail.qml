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

    GridView {
        id: priKey

        anchors {
            margins: 2
        }

        Component.onCompleted: {
            console.log(count)
            console.log(width)
            console.log (height)
        }
        clip: true
        interactive: true
        cellWidth: 110
        cellHeight: 26
        model: _device_model.device.primary_key_sequence
        delegate: Rectangle {
            id: key
            width: priKey.cellWidth
            height: priKey.cellHeight
            anchors {
                margins: 2
            }

            border {
                color: Qt.darker(palette.window, 1.2)
                width: 1
            }

            ComboBox {
                indicator: Canvas {
                    id: canvas
                    // Don't paint an indicator on the dropdown
                }

                width: 130
                model: _device_model.device.action_model
                Component.onCompleted: {
                    //currentIndex = find(model.action)
                    //console.log(currentIndex)
                }
                onActivated: {
                    console.log(priKey.currentIndex)
                    model.action = textAt(currentIndex)
                    console.log(model.action)
                }
            }
        }
    }

    KeySequence {
        id: secKey

        gridModel: _device_model.device.secondary_key_sequence
        //model: myModel
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

        Rectangle {
            id: colorAction
            anchors {
                top: ledLabel.bottom
                left: colorRect.right
                leftMargin: 10
            }

            width: childrenRect.width

            RadioButton {
                id: releasedColor
                anchors {
                    top: parent.top
                    left: parent.left
                }

                text: 'Released Color'
                font.pointSize: 12
                checked: true
                focusPolicy: Qt.StrongFocus

                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_Space || event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                        // Select this option on activation keys
                        releasedColor.checked = true
                        event.accepted = true
                    } else if (event.key === Qt.Key_Down || event.key === Qt.Key_Right) {
                        // Move to the other radio button with arrows
                        pressedColor.forceActiveFocus()
                        pressedColor.checked = true
                        event.accepted = true
                    }
                }

                onToggled: {
                    console.log('released color')
                }
            }

            RadioButton {
                id: pressedColor
                anchors {
                    top: releasedColor.bottom
                    left: parent.left
                }

                property int red: 0

                text: 'Pressed Color'
                font.pointSize: 12
                focusPolicy: Qt.StrongFocus

                Keys.onPressed: function(event) {
                    if (event.key === Qt.Key_Space || event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                        pressedColor.checked = true
                        event.accepted = true
                    } else if (event.key === Qt.Key_Up || event.key === Qt.Key_Left) {
                        releasedColor.forceActiveFocus()
                        releasedColor.checked = true
                        event.accepted = true
                    }
                }

                onToggled: {
                    console.log('pressed color')
                    redSlider.value = .25
                    greenSlider.value = .34
                    blueSlider.value = .77
                }
            }
        }

        RGBSlider {
            id: redSlider
            anchors {
                top: ledLabel.bottom
                left: colorAction.right
                leftMargin: 10
            }

            text: 'Red'
            sliderWidth: 350
        }

        RGBSlider {
            id: greenSlider
            anchors {
                top: redSlider.bottom
                left: colorAction.right
                topMargin: 10
                leftMargin: 10
            }
            text: 'Green'
            sliderWidth: 350
        }

        RGBSlider {
            id: blueSlider
            anchors {
                top: greenSlider.bottom
                left: colorAction.right
                topMargin: 10
                leftMargin: 10
            }
            text: 'Blue'
            sliderWidth: 350
        }
    }
}