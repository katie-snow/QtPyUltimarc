import QtQuick 2.0
import QtQuick.Controls 2.12


Rectangle {
    id: imageBar
    anchors {
        left: parent.left
        top: parent.top
        margins: 20
    }

    height: childrenRect.height

    Image {
        source: '../assets/ultimarctitle.jpg'
    }
}

