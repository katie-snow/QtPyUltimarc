import QtQuick 2.0
import QtQuick.Controls 2.12


Rectangle {
    id: backgroundImage
    anchors {
        left: parent.left
        verticalCenter: parent.verticalCenter
        leftMargin: 15
    }
    implicitHeight: childrenRect.height
    implicitWidth: childrenRect.width

    Image {
        source: '../assets/arcadeGameMachine.jpg'
    }
}