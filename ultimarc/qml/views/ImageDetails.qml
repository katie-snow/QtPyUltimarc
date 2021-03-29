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

import QtQuick 2.12
import QtQuick.Controls 2.12 as QQC2
import QtQuick.Layouts 1.12
import QtQuick.Window 2.12

import "../simple"
import "../complex"

Item {
    id: root
    anchors.fill: parent

    property bool focused: contentList.currentIndex === 1
    enabled: focused

    QQC2.Label {
        id: referenceLabel
        visible: false
        opacity: 0
        }

    function toMainScreen() {
        archPopover.open = false
        versionPopover.open = false
        canGoBack = false
        contentList.currentIndex--
    }

    signal stepForward

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.BackButton
        onClicked:
            if (mouse.button == Qt.BackButton)
                toMainScreen()
    }

    QQC2.ScrollView {
        activeFocusOnTab: false
        focus: true
        anchors {
            fill: parent
            leftMargin: anchors.rightMargin
        }

        Item {
            x: mainWindow.margin
            implicitWidth: root.width - 2 * mainWindow.margin
            implicitHeight: childrenRect.height + Math.round(_units.grid_unit * 3.5) + _units.grid_unit * 2

            ColumnLayout {
                y: _units.grid_unit
                width: parent.width
                spacing: _units.large_spacing * 3

                RowLayout {
                    id: tools
                    Layout.fillWidth: true
                    QQC2.Button {
                        id: backButton
                        icon.name: "qrc:/icons/go-previous"
                        text: qsTr("Back")
                        onClicked: toMainScreen()
                    }
                    Item {
                        Layout.fillWidth: true
                    }
                    QQC2.Button {
                        text: qsTr("Create Live USB…")
                        highlighted: true

                        onClicked: {
                            if (dlDialog.visible)
                                return
                            deviceNotification.open = false
                            archPopover.open = false
                            versionPopover.open = false
                            dlDialog.visible = true
                            releases.variant.download()
                        }
                        enabled: !_releases.selected.isLocal || releases.variant.iso
                    }
                }

                RowLayout {
                    z: 1 // so the popover stays over the text below
                    spacing: _units.large_spacing
                    Item {
                        Layout.preferredWidth: Math.round(_units.grid_unit * 3.5) + _units.grid_unit
                        Layout.preferredHeight: Math.round(_units.grid_unit * 3.5)
                        Layout.alignment: Qt.AlignHCenter
                        IndicatedImage {
                            anchors.fill: parent
                            x: _units.grid_unit
                            source: _devices.selected_icon ? _devices.selected_icon: ""
                            fillMode: Image.PreserveAspectFit
                            sourceSize.width: parent.width
                            sourceSize.height: parent.height
                        }
                    }
                    ColumnLayout {
                        Layout.fillHeight: true
                        spacing: _units.large_spacing
                        RowLayout {
                            Layout.fillWidth: true
                            QQC2.Label {
                                Layout.fillWidth: true
                                font.pointSize: referenceLabel.font.pointSize + 4
                                text: {_devices.selected_product_name !== "Unknown Name" ? _devices.selected_product_name :
                                       _devices.selected_device_class
                                      }
                            }
                            QQC2.Label {
                                font.pointSize: referenceLabel.font.pointSize + 2
                                text: _devices.selected_device_class
                                opacity: 0.6
                            }
                        }
                        ColumnLayout {
                            width: parent.width
                            spacing: _units.large_spacing
                            QQC2.Label {
                                font.pointSize: referenceLabel.font.pointSize + 1
                                visible: _devices.selected_connected
                                text: _devices.selected_product_key
                                opacity: 0.6
                            }
                            QQC2.Label {
                                font.pointSize: referenceLabel.font.pointSize - 1
                                visible: releases.selected.version && releases.variant
                                text: "Description"
                                opacity: 0.6
                            }
                        }
                    }
                }
                QQC2.Label {
                    Layout.fillWidth: true
                    width: Layout.width
                    wrapMode: Text.WordWrap
                    text: "Board Data"
                    textFormat: Text.RichText
                }
                Repeater {
                    id: screenshotRepeater
                    model: releases.selected.screenshots
                    ZoomableImage {
                        z: 0
                        smooth: true
                        cache: false
                        Layout.fillWidth: true
                        Layout.preferredHeight: width / sourceSize.width * sourceSize.height
                        fillMode: Image.PreserveAspectFit
                        source: modelData
                    }
                }
            }
        }
    }
}
