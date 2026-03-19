import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import SddmComponents 2.0 as SDDM

Item {
    id: root
    width: Screen.width
    height: Screen.height

    SDDM.TextConstants { id: textConstants }

    // Background Image
    Image {
        id: bgImage
        anchors.fill: parent
        source: config.background || ""
        fillMode: Image.PreserveAspectCrop
        smooth: true
        asynchronous: true
    }

    // Login Card (Glassmorphism)
    Rectangle {
        id: loginCard
        width: 420
        height: 380
        anchors.centerIn: parent
        color: Qt.rgba(
            parseInt(config.surface.substring(1,3), 16)/255.0,
            parseInt(config.surface.substring(3,5), 16)/255.0,
            parseInt(config.surface.substring(5,7), 16)/255.0,
            0.6
        )
        radius: 20
        border.width: 1
        border.color: Qt.rgba(255, 255, 255, 0.1)

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 24

            // Clock
            Text {
                id: clock
                text: Qt.formatTime(new Date(), "hh:mm")
                font.pixelSize: 64
                font.weight: Font.Bold
                color: config.on_background
                Layout.alignment: Qt.AlignHCenter

                Timer {
                    interval: 1000; running: true; repeat: true
                    onTriggered: clock.text = Qt.formatTime(new Date(), "hh:mm")
                }
            }

            // User Selection
            ComboBox {
                id: userCombo
                model: userModel
                textRole: "name"
                currentIndex: userModel.lastIndex
                Layout.preferredWidth: 260
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: 18
                
                contentItem: Text {
                    text: userCombo.currentText
                    color: config.on_background
                    font: userCombo.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: "transparent"
                    border.width: 0
                }
            }

            // Password Field
            TextField {
                id: passwordBox
                placeholderText: textConstants.password
                echoMode: TextInput.Password
                Layout.preferredWidth: 260
                Layout.preferredHeight: 50
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: 16
                color: config.on_background
                horizontalAlignment: TextInput.AlignHCenter

                background: Rectangle {
                    color: Qt.rgba(
                        parseInt(config.surface_variant.substring(1,3), 16)/255.0,
                        parseInt(config.surface_variant.substring(3,5), 16)/255.0,
                        parseInt(config.surface_variant.substring(5,7), 16)/255.0,
                        0.5
                    )
                    radius: 25
                    border.width: passwordBox.activeFocus ? 2 : 1
                    border.color: passwordBox.activeFocus ? config.primary : Qt.rgba(255, 255, 255, 0.2)
                }

                Keys.onReturnPressed: {
                    if (passwordBox.text !== "") {
                        sddm.login(userCombo.currentText, passwordBox.text, sessionModel.lastIndex)
                    }
                }
            }
            
            // Login Error Message
            Text {
                text: textConstants.prompt
                color: config.error
                font.pixelSize: 14
                opacity: 0.8
                Layout.alignment: Qt.AlignHCenter
                visible: passwordBox.text === "" && opacity > 0
            }
        }
    }

    Connections {
        target: sddm
        function onLoginSucceeded() {}
        function onLoginFailed() {
            passwordBox.text = ""
            // Trigger shake/error animation here if desired
        }
    }

    // Default Focus
    Component.onCompleted: {
        passwordBox.forceActiveFocus()
    }
}
