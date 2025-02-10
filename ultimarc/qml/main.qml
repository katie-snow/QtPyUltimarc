
import QtQuick
import QtQuick.Controls
import QtQuick.Window
import QtQuick.Layouts
import QtQml

import "complex"

Window {
    id: mainWindow
    visible: true
    minimumWidth: 1024
    minimumHeight: 680
    title: "Ultimarc Editor"
    color: palette.window

    property real margin: 50 + (width - 800) / 4

    // Temp object
    Rectangle {
        id: centerLine
        width: 1
        border.width: 1
        anchors {
            top: parent.top
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: -width / 2
        }
    }

    ImageBar {
        id: imageBar
    }

    Loader {
        id: mainLoader
        anchors {
            left: parent.left
            right: parent.right
            top: imageBar.bottom
            bottom: activateButton.top

            leftMargin: margin
            rightMargin: margin
            topMargin: 20
        }
        focus: true
        source: 'views/DeviceStackView.qml'
    }

    Button {
        id: activateButton
        anchors {
            left: parent.horizontalCenter
            bottom: parent.bottom
            horizontalCenterOffset: -width / 2
            leftMargin: 7
            topMargin: 20
            bottomMargin: 80
        }
        text: 'Next'
        highlighted: true

        function activate () {
            if (mainLoader.item.svItem.currentItem.activate_str  === 'devicesList') {
                mainLoader.item.svItem.push('views/DeviceDetails.qml')
                text = 'Back'
            }
            else {
                mainLoader.item.svItem.pop()
                text = 'Next'
            }
        }

        onClicked: activate ()
    }

    Button {
        id: aboutButton
        anchors {
            right: parent.horizontalCenter
            bottom: parent.bottom
            horizontalCenterOffset: -width / 2
            rightMargin: 12
            topMargin: 20
            bottomMargin: 80
        }
        text: 'About'
        highlighted: true
    }
}
