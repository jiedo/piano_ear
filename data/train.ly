\version "2.18.0"

#(set-default-paper-size "a4" 'landscape)
#(set-global-staff-size 50)

\paper {
   print-page-number = false
}

\header {
  tagline = "Ear training"  % removed
  title = "Music"
  composer = "Faust"

}


\score {
  \relative c' {

    \time 2/2

    \set Staff.midiInstrument = #"electric grand"

    c-"C Major Scale(Ionian)" d e f g a b c
R1
    c,4-"Lydian" d e fis g a b c
R1
    c,4-"Mixo-Lydian" d e f g a bes c

R1
R1
    c,4-"C Minor Scale(Aeolian)" d ees f g aes bes c
R1
    c,4-"C Harmonic Scale" d ees f g aes b c
R1
    c,4-"C Melodic Scale" d ees f g a b c
R1
R1
    c,4-"Dorian" d ees f g a bes c
R1
    c,4-"Phrygian" des ees f g aes bes c
R1
    c,4-"Locrian" des ees f ges aes bes c
R1
R1

% intervals:
c,2 c
c cis
c d
c dis
c e
c f
c fis
c g'
c, gis'
c, a'
c, ais'
c, b'

% interval chord:
R1

<c, c>-"Unison"
R

<c cis>-"Minor 2nd"
R

<c d>-"Major 2nd"
R

<c dis>-"Minor 3rd"
R

<c e>-"Major 3rd"
R

<c f>-"Perfect 4th"
R

<c fis>-"Tritone"
R

<c g'>-"Perfect 5th"
R

<c gis'>-"Minor 6th"
R

<c a'>-"Major 6th"
R

<c ais'>-"Minor 7th"
R

<c b'>-"Major 7nd"
R

<c c'>-"Perfect Octove"


R

% triad chord:
<c e g>-"Major Triad"
R

<c ees g>-"Minor Triad"
R

<c e gis>-"Aug. Triad"
R

<c ees ges>-"Dim."
R

<c e g bes>-"Dom.7th"
R

<c e g b>-"Major 7th"
R

<c ees g bes>-"Minor 7th"
R

<c ees ges beses>-"Dim.7th"
R

<c ees ges bes>-"Half-dim.7th"
R

<c e gis bes>-"Aug.7th"
R

<c e gis b>-"Aug-maj.7th"
R

<c ees g b>-"Min-maj.7th"
R

<c d g>-"Sus2"
R

<c f g>-"Sus4"
R

<c f g bes>-"7Sus4"
R


  }
  \layout {

  }

  \midi {
    \context {
      \Voice
      \remove Dynamic_performer
    }
  }
}