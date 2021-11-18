import QtQuick 2.4
import Qt.labs.platform 1.1

FileDialog {
    id: root

    title: "Choose file"
    defaultSuffix: "json"
    nameFilters: ["Json files (*.json)"]
}