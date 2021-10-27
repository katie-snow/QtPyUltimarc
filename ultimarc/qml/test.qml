import QtQuick 2.0
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
//import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12
import QtQml 2.12

ApplicationWindow {
    id: mainWindow
    visible: true
    minimumWidth: 800
    minimumHeight: 480
    title: "Ultimarc Editor"

    Text {
        id: text1
        text: "Hello"
        font.pixelSize: 18

        anchors {
            centerIn: parent
        }
    }

    Rectangle {
        id: threeDotWrapper
        clip: true
        visible: true
        enabled: visible
        activeFocusOnTab: true
        radius: 3
        color: 'lightblue'
        width: 24
        height: 12
        anchors.horizontalCenter: parent.horizontalCenter
        y: 59
        z: -1
        Rectangle {
            anchors.fill: parent
            anchors.topMargin: -_units.large_spacing
            color: threeDotMouse.containsPress ? Qt.darker(palette.window, 1.2) : threeDotMouse.containsMouse ? palette.window : palette.background
            Behavior on color { ColorAnimation { duration: 120 } }
            radius: 5
            border {
                color: Qt.darker(palette.background, 1.3)
                width: 1
            }
        }

        Column {
            id: threeDotDots
            property bool hidden: false
            opacity: hidden ? 0.0 : 1.0
            Behavior on opacity { NumberAnimation { duration: 60 } }
            anchors.centerIn: parent
            spacing: 2
            Repeater {
                model: 3
                Rectangle { height: 4; width: 4; radius: 1; color: mixColors(palette.windowText, palette.window, 0.75); antialiasing: true }
            }
        }

        QQC2.Label {
            id: threeDotText
            y: threeDotDots.hidden ? parent.height / 2 - height / 2 : -height
            anchors.horizontalCenter: threeDotDots.horizontalCenter
            Behavior on y { NumberAnimation { duration: 60 } }
            clip: true
            text: qsTr("Display Ultimarc Devices")
            opacity: 0.6
        }

        FocusRectangle {
            visible: threeDotWrapper.activeFocus
            anchors.fill: parent
            anchors.margins: 2
        }

        Timer {
            id: threeDotTimer
            interval: 200
            onTriggered: {
                threeDotDots.hidden = true
            }
        }

        Keys.onSpacePressed: threeDotMouse.action()
        MouseArea {
            id: threeDotMouse
            anchors.fill: parent
            acceptedButtons: Qt.AllButtons
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onHoveredChanged: {
                if (containsMouse && !pressed) {
                    threeDotTimer.start()
                }
                if (!containsMouse) {
                    threeDotTimer.stop()
                    threeDotDots.hidden = false
                }
                console.log("Hover: ", _pages.front_page, moveUp.running)
            }
            function action() {
                moveUp.enabled = true
                _pages.front_page = false
                _devices.invalidate_filter
            }
            onClicked: {
                action()
                console.log("mouseArea: ", _pages.front_page, moveUp.running)
            }
        }
    }

    ListModel {
        id: _nameModel
        ListElement { name: "Mini-pac #1"; key: "d209:0440"; device_class: "Mini-pac"}
    }

    ListView {
        id: lv1
        focus : true
        clip: true

        anchors.top: text1.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        //anchors.fill: parent
        //anchors.horizontalCenter: text1
        model : _deviceModel

        delegate: Component {
            color : "pink"
            width : parent.width
            height: childrenRect.height

            Text {
                text: "Hi " + model.class + " " + model.product_name + " " + model.product_key
                anchors.fill: parent
                font.pixelSize: 18
                Component.onCompleted: console.log("Welcome", model.index, model.product_name)
            }
        }
    }
}