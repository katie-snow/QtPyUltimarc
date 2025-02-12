import QtQuick 2.4
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.12

import "../complex"

Item {
    id: root
    anchors.fill: parent

    Label {
        id: referenceLabel
        visible: false
        opacity: 0
        width: 30
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true

        Rectangle {
            implicitWidth: mainWindow.width - margin * 2
            height: childrenRect.height + _units.large_spacing
            Layout.topMargin: 20

            color: 'transparent'
            border.color: Qt.darker(palette.window, 1.2)
            border.width: 2

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true

                Item {
                    Layout.fillWidth: true
                    implicitHeight: _units.large_spacing / 2
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    ColumnLayout {
                        Label {
                            id: selectedName
                            Layout.alignment: Qt.AlignHCenter
                            font.pointSize: referenceLabel.font.pointSize + 1
                            font.bold: true
                            text: qsTr('Pin Name')
                        }

                        RowLayout {
                            spacing: _units.large_spacing
                            Label {
                                leftPadding: _units.large_spacing + 10
                                font.pointSize: referenceLabel.font.pointSize - 1
                                text: "Debounce:"
                            }
                            ComboBox {
                                implicitWidth: 87
                                implicitHeight: 26
                                model: ['standard', 'none', 'short', 'long']
                                Component.onCompleted: {
                                    currentIndex = find(_device_model.debounce)
                                }
                                onActivated: {
                                    _device_model.debounce = textAt(currentIndex)
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.alignment: Qt.AlignTop
                        RowLayout {
                            CheckBox {
                                id: selectedShift
                                font.pointSize: referenceLabel.font.pointSize - 1
                                text: qsTr("Shift")
                            }
                            Label {
                                Layout.leftMargin: _units.large_spacing * 10
                                color: "blue"
                                font.pointSize: referenceLabel.font.pointSize - 1
                                text: "Primary Action:"
                            }
                            ComboBox {
                                id: selectedAction
                                implicitWidth: 130
                                model: _device_model.device.actions
                                onCurrentIndexChanged: {
                                    if(activeFocus) {
                                        model.action = selectedAction.textAt(currentIndex)
                                    }
                                }
                            }
                            Label {
                                color: "red"
                                font.pointSize: referenceLabel.font.pointSize - 1
                                text: "Alternative Action:"
                            }
                            ComboBox {
                                id: selectedAltAction
                                implicitWidth: 130
                                model: _device_model.device.alt_actions
                                onCurrentIndexChanged: {
                                    if (activeFocus) {
                                        model.action = selectedAltAction.textAt(currentIndex)
                                    }
                                }
                            }
                        }
                        RowLayout {
                            CheckBox {
                                id: paclink
                                font.pointSize: referenceLabel.font.pointSize - 1
                                text: qsTr("PacLink")

                                onToggled: {
                                    _device_model.device.paclink = checked
                                }
                                Component.onCompleted: {
                                    checked = _device_model.device.paclink
                                }
                            }
                            Button {
                                text: {
                                    "Macros"
                                }
                                highlighted: true
                                function macroAction () {
                                    macrosPopup.open()
                                }
                                onClicked: {
                                    macroAction()
                                }
                                Keys.onSpacePressed: macroAction()
                            }

                            MacroPopup {
                                id: macrosPopup
                                anchors.centerIn: Overlay.overlay
                                onClosed: {
                                    _device_model.device.update_macro
                                }
                            }
                        }
                    }
                }
            }
        }

        // Data Section
        RowLayout {
            Rectangle {
                Layout.alignment: Qt.AlignTop
                implicitWidth: (mainWindow.width - margin) / 6
                implicitHeight: mainWindow.height - margin * 3.75

                color: 'transparent'
                border.color: Qt.darker(palette.window, 1.2)
                border.width: 2

                ListView {
                    id: filterList

                    implicitWidth: parent.width
                    implicitHeight: parent.height
                    leftMargin: 5

                    clip: false
                    interactive: true
                    focus: true

                    highlight: Rectangle {
                        color: 'lightblue'
                        radius: 5
                    }

                    model: _device_model.device.pac_filter
                    delegate: Rectangle {
                        width: parent.width - 2
                        height: childrenRect.height
                        color: filterList.currentIndex == index ? 'lightblue' : 'transparent'

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor

                            onClicked: {
                                filter_action ()
                            }

                            function filter_action () {
                                filterList.currentIndex = index
                                _device_model.device.pin_filter.filter = model.filter
                            }
                        }
                        Text {
                            text: model.name
                        }
                    }
                }
            }

            Rectangle {
                Layout.alignment: Qt.AlignTop
                //Layout.margins: 10
                implicitWidth: mainWindow.width - margin * 3.5
                implicitHeight: mainWindow.height - margin * 3.75

                color: 'transparent'
                border.color: Qt.darker(palette.window, 1.2)
                border.width: 2

                GridView {
                    id: grid

                    implicitWidth: parent.implicitWidth
                    implicitHeight: parent.implicitHeight - 4
                    leftMargin: 4
                    topMargin: 4

                    clip: true
                    interactive: true

                    cellWidth: 104
                    cellHeight: 46

                    model: _device_model.device.pin_filter
                    delegate: Rectangle {
                        width: grid.cellWidth - 1
                        height: grid.cellHeight - 1

                        color: {
                            detailMouse.containsPress ? Qt.darker(palette.button, 1.2) : palette.window
                        }
                        border {
                            color: Qt.darker(palette.window, 1.2)
                            width: 1
                        }
                        MouseArea {
                            id: detailMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            function mouseAction() {
                                grid.currentIndex = index
                                // Make sure the grid has the focus again
                                grid.focus = true

                                selectedName.text = model.name
                                selectedShift.checked = model.shift
                                selectedAction.currentIndex = selectedAction.find(model.action, Qt.MatchFixedString)
                                selectedAltAction.currentIndex = selectedAltAction.find(model.alt_action, Qt.MatchFixedString)
                            }
                            onClicked: {
                                mouseAction()
                            }
                            // Not the best way to do this, but it gets the job done.  Setting the first pin
                            // as the selected pin
                            Component.onCompleted: {
                                if (index == 0) {
                                    mouseAction()
                                }
                            }
                        }
                        ColumnLayout {
                            spacing: 1
                            RowLayout {
                                Layout.fillHeight: true
                                Layout.fillWidth: true
                                Label {
                                    id: pinName
                                    leftPadding: 3
                                    font.pointSize: referenceLabel.font.pointSize + 1
                                    font.bold: true
                                    text: qsTr(model.name)
                                }
                                Item {
                                    Layout.fillWidth: true
                                }
                                Label {
                                    id: shift
                                    text: qsTr("Shift")
                                    font.pointSize: referenceLabel.font.pointSize - 1
                                    rightPadding: 5
                                    font.bold: { model.shift }

                                    Connections {
                                        target: selectedShift
                                        function onCheckedChanged() {
                                            if (grid.currentIndex == index && selectedShift.activeFocus) {
                                                model.shift = selectedShift.checked
                                            }
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                Layout.preferredWidth: 98
                                height: childrenRect.height
                                Layout.margins: 1

                                RowLayout {
                                    spacing: 0

                                    Rectangle {
                                        width: childrenRect.width
                                        height: childrenRect.height
                                        color: "transparent"

                                        Label {
                                            id: action
                                            color: "blue"
                                            bottomPadding: 1
                                            leftPadding: 1
                                            width: 49
                                            font.pointSize: referenceLabel.font.pointSize
                                            text: model.action
                                            font.bold: true
                                            elide: Text.ElideRight

                                            Connections {
                                                target: selectedAction
                                                function onCurrentIndexChanged() {
                                                    if (grid.currentIndex == index && selectedAction.activeFocus) {
                                                        model.action = selectedAction.textAt(selectedAction.currentIndex)
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    Rectangle {
                                        width: childrenRect.width
                                        height: childrenRect.height
                                        color: "transparent"

                                        Label {
                                            id: altAction
                                            color: "red"
                                            bottomPadding: 1
                                            leftPadding: 3
                                            width: 49
                                            font.pointSize: referenceLabel.font.pointSize
                                            text: model.alt_action
                                            font.bold: true
                                            elide: Text.ElideRight

                                            Connections {
                                                target: selectedAltAction
                                                function onCurrentIndexChanged() {
                                                    if (grid.currentIndex == index && selectedAltAction.activeFocus) {
                                                        model.alt_action = selectedAltAction.textAt(selectedAltAction.currentIndex)
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}