set xrange [0:1]
set yrange [-40:1]
set title "p1 Plot"
plot 'p1_0.txt' with points pt 7 linecolor "red" title 'alpha=0', 'p1_1.txt' with points pt 7 linecolor "blue" title 'alpha=0.1', 'p1_2.txt' with points pt 7 linecolor "black" title 'alpha=1', 'p1_3.txt' with points pt 7 linecolor "yellow" title 'alpha=3'

