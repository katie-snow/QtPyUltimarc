/*
 * Fedora Media Writer
 * Copyright (C) 2016 Martin Bříza <mbriza@redhat.com>
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

import QtQuick 2.2
import QtQuick.Controls 2.2 as QQC2
import QtQuick.Layouts 1.12

import "../simple"
import "../complex"

FocusScope {
    id: imageList

    property alias currentIndex: devicesListView.currentIndex
    property real fadeDuration: 200

    property bool focused: contentList.currentIndex === 0
    signal stepForward(int index)

    enabled: focused

    anchors.fill: parent
    clip: true

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.ForwardButton
        onClicked: {
            if (lastIndex >= 0 && mouse.button == Qt.ForwardButton)
                stepForward(lastIndex)
        }
    }

    // this has to be here for softwarecontext (clipping is a bit broken)
    Rectangle {
        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
            bottom: searchBoxRow.bottom
            rightMargin: fullList.viewport ? fullList.width - fullList.viewport.width : 0
        }
        z: -1
        color: palette.window
    }

    RowLayout {
        id: searchBoxRow
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            topMargin: 12
            leftMargin: mainWindow.margin
            rightMargin: mainWindow.margin + 1
        }
        spacing: 4

        QQC2.TextField {
            id: searchBox
            Layout.fillWidth: true
            z: 2
            enabled: !_pages.front_page
            opacity: !_pages.front_page ? 1.0 : 0.0
            visible: opacity > 0.0
            activeFocusOnTab: visible
            placeholderText: qsTr("Find an Ultimarc Configuration")
            text: _devices_filter.filter_text
            onTextChanged: _devices_filter.filter_text = text
            clip: true

            Behavior on opacity {
                NumberAnimation {
                    duration: imageList.fadeDuration
                }
            }
        }

        QQC2.ComboBox {
            id: deviceClassSelect
            enabled: !_pages.front_page
            opacity: !_pages.front_page ? 1.0 : 0.0
            activeFocusOnTab: visible
            visible: opacity > 0.0
            model: _device_class_model
            textRole: "class_name"
            valueRole: "class_value"

            onActivated:  {
                _class_filter.filter = currentValue
            }

            Behavior on opacity {
                NumberAnimation {
                    duration: imageList.fadeDuration
                }
            }
        }
    }

    Rectangle {
        id: whiteBackground

        z: -1
        clip: true
        radius: 6
        color: "transparent"
        y: _pages.front_page || moveUp.running ? parent.height / 2 - height / 2 : 54
        Behavior on y {
            id: moveUp
            enabled: false

            NumberAnimation {
                onStopped: moveUp.enabled = false
            }
        }
        height: _pages.front_page ? adjustedHeight(_devices.count) : parent.height
        anchors {
            left: parent.left
            right: parent.right
            rightMargin: mainWindow.margin
            leftMargin: anchors.rightMargin
        }

        function adjustedHeight(count) {
            var height = Math.round(_units.grid_unit * 4.5) * count + (_units.grid_unit * 2)
            if (height % 2) {
                return height + 1
            } else {
                return height
            }
        }
    }

    QQC2.ScrollView {
        id: fullList
        anchors {
            fill: parent
            topMargin: whiteBackground.y
        }

        ListView {
            id: devicesListView
            anchors {
                fill: parent
                leftMargin: mainWindow.margin
                rightMargin: mainWindow.margin
            }

            clip: true
            focus: true
            model: _devices_filter

            delegate: DelegateDevice {
                width: devicesListView.width
                focus: true
            }

            remove: Transition {
                NumberAnimation { properties: "x"; to: width; duration: 300 }
            }
            removeDisplaced: Transition {
                NumberAnimation { properties: "x,y"; duration: 300 }
            }
            add: Transition {
                NumberAnimation { properties: _pages.front_page ? "y" : "x"; from: _pages.front_page ? 0 : -width; duration: 300 }
            }
            addDisplaced: Transition {
                NumberAnimation { properties: "x,y"; duration: 300 }
            }

            section {
                property: "category"
                criteria: ViewSection.FullString
                labelPositioning: ViewSection.InlineLabels
                delegate: Item {
                    height: section == "main" ? 0 : Math.round(_units.grid_unit * 3.5)
                    width: parent.width
                    QQC2.Label {
                        text: section
                        textFormat: Text.RichText
                        anchors {
                            left: parent.left
                            bottom: parent.bottom
                            leftMargin: _units.grid_unit
                            bottomMargin: _units.large_spacing + _units.small_spacing
                        }
                    }
                }
            }

            footer: Item {
                id: footerRoot
                height: !_pages.front_page ? aboutColumn.height + (_units.grid_unit * 4) : _units.grid_unit * 2
                width: devicesListView.width
                z: 0
                Column {
                    id: aboutColumn
                    width: parent.width
                    visible: !_pages.front_page
                    spacing: 0
                    Item {
                        width: parent.width
                        height: Math.round(_units.grid_unit * 3.5)

                        QQC2.Label {
                            anchors {
                                bottom: parent.bottom
                                left: parent.left
                                leftMargin: _units.grid_unit
                                bottomMargin: _units.large_spacing + _units.small_spacing
                            }
                            text: qsTr("About Ultimarc Editor")
                        }
                    }
                    Rectangle {
                        width: parent.width
                        radius: 5
                        color: palette.background
                        border {
                            color: Qt.darker(palette.background, 1.3)
                            width: 1
                        }
                        height: childrenRect.height + Math.round(_units.grid_unit * 1.3)
                        Behavior on height { NumberAnimation {} }
                        Column {
                            id: aboutLayout
                            spacing: _units.small_spacing
                            y: _units.large_spacing + _units.small_spacing
                            x: _units.grid_unit * 2
                            width: parent.width
                            move: Transition { NumberAnimation { properties: "y" } }

                            QQC2.Label {
                                width: parent.width
                                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                                text: qsTr("Version %1").arg(_ultimarc_version)
                                textFormat: Text.RichText
                            }

                            QQC2.Label {
                                width: parent.width
                                wrapMode: Text.WrapAtWordBoundaryOrAnywhere
                                text: qsTr("Please report bugs or your suggestions on %1").arg("<a href=\"https://github.com/katie-snow/QtPyUltimarc/issues\">https://github.com/katie-snow/QtPyUltimarc/</a>")
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
                }
            }

            Rectangle {
                id: threeDotWrapper
                clip: true
                visible: _pages.front_page
                enabled: visible
                activeFocusOnTab: true
                radius: 3
                color: palette.window
                width: devicesListView.width - 2
                height: _units.grid_unit * 2
                anchors.horizontalCenter: parent.horizontalCenter
                y: Math.round(_units.grid_unit * 4.5) * _devices.count + 1
                z: 1
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
                    spacing: _units.small_spacing
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

                Rectangle {
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
                    }
                    onClicked: {
                        action()
                    }
                    function action() {
                        moveUp.enabled = true
                        _pages.front_page = false
                        _devices_filter.invalidate_filter
                    }
                }
            }
        }
    }
}
