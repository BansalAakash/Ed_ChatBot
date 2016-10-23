package com.google.firebase.codelab.friendlychat;

import android.app.ActionBar;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.v4.app.NavUtils;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.auth.UserProfileChangeRequest;

import static android.R.attr.name;

/**
 * Created by hp on 15-09-2016.
 */

public class SignUpActivity extends AppCompatActivity implements View.OnClickListener {
    private static final String TAG = "SignUpActivity";
    String name;
    private FirebaseAuth mAuth;
    private FirebaseAuth.AuthStateListener mAuthListener;
    private EditText editText1;
    private EditText editText2;
    private int maleflag = 0;
    private int femaleflag = 0;
    private EditText editText3;
    private UserProfileChangeRequest profileUpdates;
    private Button button1;
    private RadioGroup gender;
// ...

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setStatusBarTranslucent(true);

        setContentView(R.layout.activity_sign_up);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        editText1 = (EditText) findViewById(R.id.name_edittext);
        editText2 = (EditText) findViewById(R.id.email_edittext);
        editText3 = (EditText) findViewById(R.id.password_edittext);
        button1 = (Button) findViewById(R.id.register_button);
        gender = (RadioGroup) findViewById(R.id.gender_radio);
        mAuth = FirebaseAuth.getInstance();
        mAuthListener = new FirebaseAuth.AuthStateListener() {
            @Override
            public void onAuthStateChanged(@NonNull FirebaseAuth firebaseAuth) {
                FirebaseUser user = firebaseAuth.getCurrentUser();
                if (user != null) {
                    // User is signed in
                    Log.d(TAG, "onAuthStateChanged:signed_in:" + user.getUid());
                    String photoURI_male = "http://www.iconsfind.com/wp-content/uploads/2015/08/20150831_55e46b00e9b98.png";
                    String photoURI_female = "https://t4.ftcdn.net/jpg/01/05/72/55/240_F_105725550_LsQIhnhtWkmUfJ7XMyFWAjTxtmsdlICx.jpg";
                    if (maleflag == 1) {
                        profileUpdates = new UserProfileChangeRequest.Builder()
                                .setDisplayName(name)
                                .setPhotoUri(Uri.parse(photoURI_male))
                                .build();
                        Toast.makeText(SignUpActivity.this, "Male done!" + name, Toast.LENGTH_SHORT).show();
                    } else if (femaleflag == 1) {
                        profileUpdates = new UserProfileChangeRequest.Builder()
                                .setDisplayName(name)
                                .setPhotoUri(Uri.parse(photoURI_female))
                                .build();
                        Toast.makeText(SignUpActivity.this, "Female done!" + name, Toast.LENGTH_SHORT).show();
                    }

                    user.updateProfile(profileUpdates)
                            .addOnCompleteListener(new OnCompleteListener<Void>() {
                                @Override
                                public void onComplete(@NonNull Task<Void> task) {
                                    if (task.isSuccessful()) {
                                        Log.d(TAG, "User profile updated.");
                                        Toast.makeText(SignUpActivity.this, "Sign up successful" + name, Toast.LENGTH_SHORT).show();
                                        FirebaseAuth.getInstance().signOut();
                                        startActivity(new Intent(SignUpActivity.this, SignInActivity.class));
                                        finish();
                                    }
                                }
                            });
                } else {
                    // User is signed out
                    Log.d(TAG, "onAuthStateChanged:signed_out");
                    ;
                }
            }
        };
        button1.setOnClickListener(this);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            // Respond to the action bar's Up/Home button
            case android.R.id.home:
                startActivity(new Intent(SignUpActivity.this, SignInActivity.class));
                finish();
                return true;
        }
        return super.onOptionsItemSelected(item);
    }

    protected void setStatusBarTranslucent(boolean makeTranslucent) {
        if (makeTranslucent) {
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
        } else {
            getWindow().clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
        }
    }

    private int checkformcomplete() {
        int flag = 1;
        name = editText1.getText().toString().trim();
        String email = editText2.getText().toString().trim();
        String password = editText3.getText().toString().trim();
        int radiostatus = gender.getCheckedRadioButtonId();
        if (name.equals("")) {
            flag = 0;
            editText1.setError("This field is mandatory!");
        }
        if (email.equals("")) {
            flag = 0;
            editText2.setError("This field is mandatory!");
        }
        if (password.equals("")) {
            flag = 0;
            editText3.setError("This field is mandatory!");
        }
        if (radiostatus == -1) {
            flag = 0;
            RadioButton radioid = (RadioButton) findViewById(R.id.radio_female);
            radioid.setError("This field is mandatory!");
        }
        return flag;
    }

    private void signUp() {
        name = editText1.getText().toString().trim();
        String email = editText2.getText().toString().trim();
        String password = editText3.getText().toString().trim();
        int radiostatus = gender.getCheckedRadioButtonId();
        mAuth.createUserWithEmailAndPassword(email, password)
                .addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
                    @Override
                    public void onComplete(@NonNull Task<AuthResult> task) {
                        Log.d(TAG, "createUserWithEmail:onComplete:" + task.isSuccessful());
                        // If sign in fails, display a message to the user. If sign in succeeds
                        // the auth state listener will be notified and logic to handle the
                        // signed in user can be handled in the listener.
                        if (!task.isSuccessful()) {
                            Toast.makeText(SignUpActivity.this, "Sign up failed!",
                                    Toast.LENGTH_SHORT).show();
                        }
                    }
                });
    }


    @Override
    public void onStart() {
        super.onStart();
        mAuth.addAuthStateListener(mAuthListener);
    }

    @Override
    public void onStop() {
        super.onStop();
        if (mAuthListener != null) {
            mAuth.removeAuthStateListener(mAuthListener);
        }
    }

    @Override
    public void onClick(View v) {
        switch (v.getId()) {
            case R.id.register_button:
                switch (gender.getCheckedRadioButtonId()) {
                    case R.id.radio_male:
                        maleflag = 1;
                        break;
                    case R.id.radio_female:
                        femaleflag = 1;
                        break;
                }
                if (checkformcomplete() == 1)
                    signUp();
                break;
        }
    }
}
