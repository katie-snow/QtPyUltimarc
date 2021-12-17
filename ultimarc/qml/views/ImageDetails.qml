import QtQuick 2.4
import QtQuick.Controls 2.12 as QQC2
import QtQuick.Layouts 1.15

import "../complex"

Item {
    id: deviceDetails
    anchors.fill: parent

    signal stepForward

    ListView {
        id: detailList
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            rightMargin: mainWindow.margin + 1
        }

        clip: true
        focus: true

        model: _devices.device_model
        delegate: DelegateDetail {
            focus: true
        }
    }
}