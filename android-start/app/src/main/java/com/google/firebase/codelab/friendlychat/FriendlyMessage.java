package com.google.firebase.codelab.friendlychat;

/**
 * Created by hp on 7-09-2016.
 */

public class FriendlyMessage {

    private String text;
    private String name;
    private String photoUrl;
    private String timeStamp;

    public FriendlyMessage() {
    }

    public FriendlyMessage(String text, String name, String photoUrl, String timeStamp1) {
        this.text = text;
        this.name = name;
        this.photoUrl = photoUrl;
        this.timeStamp = timeStamp1;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getPhotoUrl() {
        return photoUrl;
    }

    public void setPhotoUrl(String photoUrl) {
        this.photoUrl = photoUrl;
    }

    public String getTimeStamp() {
        return timeStamp;
    }

    public void setTimeStamp(String timeStamp) {
        this.timeStamp = timeStamp;
    }
}
