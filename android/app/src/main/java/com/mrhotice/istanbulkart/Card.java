package com.mrhotice.istanbulkart;

public class Card {
    public final String word;
    public final String russian;
    public final String transcription;
    public final String ipa;
    public final String level;

    public Card(String word, String russian, String transcription, String ipa, String level) {
        this.word = word;
        this.russian = russian;
        this.transcription = transcription;
        this.ipa = ipa;
        this.level = level;
    }
}
