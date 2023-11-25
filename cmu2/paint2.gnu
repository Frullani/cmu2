set xrange [0:1]
set yrange [-4:1]
set title "x2 Plot"
plot 'x2_0.txt' with points pt 7 linecolor "red" title 'alpha=0', 'x2_1.txt' with points pt 7 linecolor "blue" title 'alpha=0.1', 'x2_2.txt' with points pt 7 linecolor "black" title 'alpha=1', 'x2_3.txt' with points pt 7 linecolor "yellow" title 'alpha=3'

