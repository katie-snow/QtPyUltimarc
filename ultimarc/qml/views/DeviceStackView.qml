import QtQuick 2.0
import QtQuick.Controls 2.12

Item {
    property alias svItem: stackview
    anchors.fill: parent
    StackView {
        id: stackview
        anchors.fill: parent
        initialItem: "DeviceList.qml"
        focus: true
    }
}
