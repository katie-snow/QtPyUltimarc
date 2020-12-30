import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.12
import QtQml 2.12

ApplicationWindow {
    id: mainWindow
    visible: true
    minimumWidth: 800
    minimumHeight: 480
    title: "Ultimarc Device Configuration Tool"

    Rectangle {
        id: root
        color: "#ffffff"
        visible: true
        property int globalMargin: 20
        width: 760
        height: 440
        anchors.margins: none.none

        Rectangle {
            id: page01
            color: "gray"
            anchors.margins: root.globalMargin
            anchors.fill: parent
        }
    }

}

/*##^##
Designer {
    D{i:0;autoSize:true;height:500;width:640}D{i:2;anchors_height:200;anchors_width:200;anchors_x:8;anchors_y:8}
D{i:1;anchors_height:500;anchors_width:640;anchors_x:0;anchors_y:0}
}
##^##*/
