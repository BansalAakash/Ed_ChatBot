package com.google.firebase.codelab.friendlychat;

import android.app.Activity;
import android.app.IntentService;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;

import java.util.ArrayList;

import static android.R.id.message;
import static com.facebook.FacebookSdk.getApplicationContext;

/**
 * Created by hp on 20-10-2016.
 */

public class IntentFiringActivity extends Activity {
    private static final String TAG = "IntentFiringActivity";
    private String intentName;
    private String[] intentFields;
    private Activity activity;
    private int response1;

    public IntentFiringActivity(String name, String fields) {
        this.intentName = name;
        this.intentFields = fields.split("\\$");
        if (this.intentName.equals("gmail")) {
            Log.d(TAG, "IntentFiringActivity length: " + Integer.toString(this.intentFields.length));
            Log.d(TAG, "IntentFiringActivity debug: " + this.intentFields[0]);
            fireGmailIntent(this.intentFields);
        }
    }

    private void fireGmailIntent(String[] intentFields) {
        String[] email = new String[1];
        email[0] = intentFields[0];
        Log.d(TAG, "My unique log " + email[0]);
        String subject = intentFields[1];
        String body = intentFields[2];
        Intent intent = new Intent(Intent.ACTION_SENDTO);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        intent.setType("message/rfc822");
        intent.setData(Uri.parse("mailto:"));
        intent.putExtra(Intent.EXTRA_EMAIL, email);
        intent.putExtra(Intent.EXTRA_SUBJECT, subject);
        intent.putExtra(Intent.EXTRA_TEXT, body);
        Log.d(TAG, "My unique log " + email[0] + "__" + subject + "__" + body);
        if (intent.resolveActivity(getPackageManager()) != null) {
            startActivity(intent);
            Log.d(TAG, "My unique log " + email[0] + "__" + subject + "__" + body + "again");
        }
    }
}