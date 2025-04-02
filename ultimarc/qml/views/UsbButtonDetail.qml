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
}