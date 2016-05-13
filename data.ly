%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Simple template for Czerny 599
% 车尔尼599简单模板
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\version "2.10.25"
\header {
  tagline = ""  % removed
}

%%%%%%%%%%%%%%
%  右手部分  %
%%%%%%%%%%%%%%
upperA = \relative c'
{
    \clef treble
    \key g \major
    \time 4/4
    \override Score.MetronomeMark #'transparent = ##t
    \tempo 4=80
    %TODO: 下面开始写右手部分

\repeat volta 2 {
    b8 d d d  e g e d

    \bar "|"
    g g g e16 d   d2

    \bar "|"
    b'8 b b b  c b a g

    \bar "|"
    a16 a a a  a8 b a2

    \bar "|"
    b8 b b16 b8 b16   c8 b a g

    \bar "|"
    e g g e16 d   d2

    \bar "|"
    b'8 b b16 b8 b16   c8 b a g

    \bar "|"
    d16 d d d  a'8 f g2

}
\repeat volta 2 {

    \bar "|"
    f4 f8 g  a4 d,4

    \bar "|"
    g8 d g a  b4 a

    \bar "|"
    c8  c4  b8  a g f g

    \bar "|"
    a4. b8 a2

    \bar "|"
    b4. b8 c4 c8 a

    \bar "|"
    b8. a16 g8 f e2

    \bar "|"
    d8 d r4 g8 g r4

    \bar "|"
    a4 g a g8 a

    \bar "|"
    b4 d8 c b4. g8

    \bar "|"
    f4 g8 a g2
}

}



%%%%%%%%%%%%%%
%  左手部分  %
%%%%%%%%%%%%%%
lowerA = \relative c
{
    \clef bass
    \key g \major
    \time 4/4
    %TODO: 下面开始写左手部分

\repeat volta 2 {
    d8 <b' g> d, <b' g>  e, <b' g> e, <b' g>

    \bar "|"
    e, <c' g> e, <c' g>  d, <a' f> d, <a' f>

    \bar "|"
    d, <b' g> d, <b' g>  d, <b' g> d, <b' g>

    \bar "|"
    d, <a' f> d, <a' f>  d, <a' f> d, <a' f>

    \bar "|"
    d, <b' g> d, <b' g>  d, <b' g> d, <b' g>

    \bar "|"
    c, <e g> c <e g>  d <a' f> d, <a' f>

    \bar "|"
    d, <b' g> d, <b' g>  d, <b' g> d, <b' g>

    \bar "|"
    d, <c' a> d, <c' a>  g <d' b> g, <d' b>

}


\repeat volta 2 {
    \bar "|"
    d, <a' f> d, <a' f>  d, <a' f> d, <a' f>

    \bar "|"
    d, <b' g> d, <b' g>  d, <b' g> d, <a' f>

    \bar "|"
    e <c' a> e, <c' a>  e, <c' a> d, <b' g>

    \bar "|"
    d, <a' f> d, <a' f>  d, <a' f> d, <a' f>

    \bar "|"
    d, <b' g> d, <b' g>  e, <c' a> e, <c' a>

    \bar "|"
    e, <b' g> e, <b' g>  e, <b' g> e, <b' g>

    \bar "|"
    <b g d>  <b g d> r4  <b g d>8 <b g d> r4

    \bar "|"
    e,8 <c' a> e, <c' a>  e, <c' a> e, <c' a>

    \bar "|"
    d, <b' g> d, <b' g>  d, <b' g> d, <b' g>

    \bar "|"
    d, <c' a> d, <c' a>  g <d' b> <d b g>4
    }

}


\score
{
    \context PianoStaff
    <<
        %\set PianoStaff.instrumentName = \markup { \fontsize #+3 \bold "1." }
        \new Staff = "up"   \upperA
        \new Staff = "down" \lowerA
    >>

    \layout { }

    \midi
    {
        \context
        {
            \Voice
            \remove Dynamic_performer
        }
    }
}