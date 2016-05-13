\version "2.18.0"

% #(set-default-paper-size "a4" 'landscape)
#(set-global-staff-size 50)

\paper {
   print-page-number = false
}

\header {
  tagline = "jiedo"  % removed
  title = "Music"
  composer = "Faust"
}


\score {
  \relative c' {

    \set Staff.midiInstrument = #"electric grand"

    <c e g>4  <c f g> c d

    b'16 b8 b16 e'
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