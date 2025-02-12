import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root

    height: 250
    width: 400
    modal: true
    focus: true
    clip: true

    closePolicy: Popup.CloseOnEscape
    standardButtons: Dialog.Ok

    title: ' '

    Rectangle {
        anchors.fill: parent
        color:  'lavender'

        Label {
            id: title
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 20
            text: 'About Ultimarc Editor'
            font.pointSize: 16
        }

        Label {
            id: version
            anchors {
                horizontalCenter: parent.horizontalCenter
                top: title.bottom
                topMargin: 10
            }

            text: 'Version ' + _version
        }

        Label {
            id: reportText
            anchors {
                horizontalCenter: parent.horizontalCenter
                top: version.bottom
                topMargin: 20
            }

            text: 'Please report bugs or suggestions on'
        }

        Label {
            id: reportLink
            anchors {
                horizontalCenter: parent.horizontalCenter
                top: reportText.bottom
                topMargin: 10
                bottomMargin: 20
            }

            text: '<a href=\"https://github.com/katie-snow/QtPyUltimarc/issues\">https://github.com/katie-snow/QtPyUltimarc/</a>'

            textFormat: Text.RichText
            onLinkActivated: Qt.openUrlExternally(link)
            opacity: 0.6

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton
                cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
            }
        }
    }
}
