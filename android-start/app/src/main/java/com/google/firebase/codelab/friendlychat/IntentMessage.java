package com.google.firebase.codelab.friendlychat;

/**
 * Created by hp on 25-09-2016.
 */

public class IntentMessage {
    private String intentName;
    private String intentFields;

    public IntentMessage() {

    }

    public IntentMessage(String a, String b) {
        this.intentName = a;
        this.intentFields = b;
    }

    public String getIntentName() {
        return intentName;
    }

    public void setIntentName(String intentName) {
        this.intentName = intentName;
    }

    public String getIntentFields() {
        return intentFields;
    }

    public void setIntentFields(String intentFields) {
        this.intentFields = intentFields;
    }
}
