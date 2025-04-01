import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

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
                keyStack.push(priKey)
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
                keyStack.push(secKey)
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

    Component {
        id: priKey

        GridView {
            id: keySequenceGrid
            anchors {
                margins: 2
            }

            clip:true
            interactive: true
            cellWidth: 113
            cellHeight: 30

            model: _device_model.device.primary_key_sequence
            delegate: Rectangle {
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
                    currentIndex: -1

                    model: _device_model.device.primary_key_sequence.actions
                    onCurrentIndexChanged: {
                        if(activeFocus) {
                            model.textAt = action.textAt(currentIndex)
                        }
                    }
                }
            }
        }
    }

    Component {
        id: secKey

        GridView {
            id: keySequenceGrid
            anchors {
                margins: 2
            }

            clip:true
            interactive: true
            cellWidth: 113
            cellHeight: 30

            model: _device_model.device.secondary_key_sequence
            delegate: Rectangle {
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
                    currentIndex: -1

                    model: _device_model.device.secondary_key_sequence.actions
                    onCurrentIndexChanged: {
                        if(activeFocus) {
                            model.textAt = action.textAt(currentIndex)
                        }
                    }
                }
            }
        }
    }
}