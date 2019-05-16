def or_re(*args: str) -> str:
    return r"({})".format("|".join(args))


word_separator_re = r"(\s|_|#)*"
practica_re = r"P(r(a|á)ctica)?"
uno_re = r"(0?1|uno)"
dos_re = r"(0?2|dos)"
tres_re = r"(0?3|tres)"
cuatro_re = r"(0?4|cuatro)"
cinco_re = r"(0?5|cinco)"
seis_re = r"(0?6|seis)"
siete_re = r"(0?7|siete)"
ocho_re = r"(0?8|ocho)"
nueve_re = r"(0?9|nueve)"
lbd_end_files = r""
images_end_files = r""
# lbd_end_files = r".*(\.(sql|txt|zip|rar))$"
# images_end_files = r".*(\.(png|jpg|jpeg|gif))$"
practice_possible_names_re = or_re(practica_re, r"tarea", r"sqlquery")
pia_possible_names_re = or_re(r"{}{}{}".format(practica_re, word_separator_re, nueve_re), r"pia",
                              r"final")
p1_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, uno_re, lbd_end_files)
p2_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, dos_re, lbd_end_files)
p3_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, tres_re, images_end_files)
p4_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, cuatro_re, lbd_end_files)
p5_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, cinco_re, lbd_end_files)
p6_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, seis_re, lbd_end_files)
p7_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, siete_re, lbd_end_files)
p8_re = r"{}{}{}{}".format(practice_possible_names_re, word_separator_re, ocho_re, lbd_end_files)
pia_re = r"{}{}".format(pia_possible_names_re, lbd_end_files)