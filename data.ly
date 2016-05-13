\version "2.18.0"



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