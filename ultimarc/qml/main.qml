
import QtQuick 6.6
import QtQuick.Controls 6.6
import QtQuick.Window 6.6
import QtQuick.Layouts 6.6
import QtQml 6.6

import "complex"

Window {
    id: mainWindow
    visible: true
    minimumWidth: 1024
    minimumHeight: 680
    title: "Ultimarc Editor"

    // Set palette items to the light theme
    // Buttons and a few other button related controls are implementing the bark background even though the code
    // says that it will be a light backgroup
    palette.base: Qt.lighter('lightblue', 1.5)
    palette.alternateBase: 'white'
    palette.window: 'white'
    palette.windowText: 'black'
    palette.text: 'black'
    palette.button: Qt.lighter('lightblue', 1.5)
    palette.buttonText: 'black'


    property real margin: 50 + (width - 800) / 4

    // Used to show center line
    Rectangle {
        id: centerLine
        width: 1
        visible: false
        border.width: 2
        anchors {
            top: parent.top
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter
            horizontalCenterOffset: -width / 2
        }
    }
    Rectangle {
        id: centerLine2
        height: 1
        border.width: 2
        visible: false
        anchors {
            left: parent.left
            right: parent.right
            verticalCenter: parent.verticalCenter
            verticalCenterOffset: height / 2
        }
    }

    BackgroundImage {
        id: backgroundImage
    }

    ImageBar {
        id: imageBar
    }


    Rectangle {
        anchors {
            left: backgroundImage.right
            right: parent.right
            top: imageBar.bottom
            bottom: activateButton.top

            rightMargin: 20
            topMargin: 20
            bottomMargin: 20
        }

        Loader {
            id: mainLoader
            anchors {
                fill: parent
            }
            focus: true
            source: 'views/DeviceStackView.qml'
        }
    }

    Button {
        id: activateButton
        anchors {
            left: parent.horizontalCenter
            bottom: parent.bottom
            horizontalCenterOffset: -width / 2
            leftMargin: 7
            topMargin: 20
            bottomMargin: 40
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
            bottomMargin: 40
        }
        text: 'About'
        highlighted: true
        function activate () {
            aboutDialog.open ()
        }

        onClicked: activate ()
    }

    AboutDialog {
        id: aboutDialog
        anchors.centerIn: Overlay.overlay
    }
}
