"""Writes content/71-es-siguiente.html, the Spanish /next, from content/70-next.html.

The English page is the source: markup, demos and votes are shared (same round,
same feature ids, so votes add up), and this table swaps the words. Run by
build.py before it reads content/. A pair whose English text is no longer on
the page fails the build, so an edit to the English page can't silently leave
the Spanish one in English.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "content", "70-next.html")
OUT = os.path.join(ROOT, "content", "71-es-siguiente.html")

# (English, Spanish). Each English text must appear on the page; every
# occurrence is replaced. Longer strings first where one contains another.
PAIRS = [
    # header
    ("title: What should Gentleskin build next? | Gentleskin", "title: ¿Qué debería agregar Gentleskin? | Gentleskin"),
    ("description: What Gentleskin, the skin picking app, could build next: small games for your hands, a progress calendar and a notebook. Try them in your browser and vote.",
     "description: Lo que Gentleskin, la app para la dermatilomanía, podría agregar: juegos chiquitos para tus manos, un calendario de avance y un cuaderno. Pruébalos en el navegador y vota."),
    # 1 something for your hands (the games shelf)
    ('aria-label="Games"', 'aria-label="Juegos"'),
    ('aria-label="Sound on" title="Sound on" hidden></button>', 'aria-label="Sonido" title="Sonido" hidden></button>'),
    ('const label = Snd.on ? "Sound on" : "Sound off";', 'const label = Snd.on ? "Sonido activado" : "Sonido apagado";'),
    ('data-g="fit" aria-selected="true">Fit</button>', 'data-g="fit" aria-selected="true">Encajar</button>'),
    ('data-g="merge" aria-selected="false">Merge</button>', 'data-g="merge" aria-selected="false">Juntar</button>'),
    ('data-g="slide" aria-selected="false">Slide out</button>', 'data-g="slide" aria-selected="false">Sacar</button>'),
    ('data-g="eels" aria-selected="false">Untangle</button>', 'data-g="eels" aria-selected="false">Desenredar</button>'),
    ('data-g="shave" aria-selected="false">Shave</button>', 'data-g="shave" aria-selected="false">Raspar</button>'),
    ('data-g="bumps" aria-selected="false">Bumps</button>', 'data-g="bumps" aria-selected="false">Bultitos</button>'),
    ('data-g="pour" aria-selected="false">Pour</button>', 'data-g="pour" aria-selected="false">Verter</button>'),
    ("Drag a piece onto the board. A full row or column clears.", "Arrastra una pieza al tablero. Una fila o columna llena se borra."),
    ("Move along the top and let go to drop a pod. Two the same size become one bigger pod.", "Muévete por arriba y suelta para dejar caer una bolita. Dos del mismo tamaño se juntan en una más grande."),
    ("Drag each block out through the door of its colour.", "Arrastra cada bloque hacia afuera por la puerta de su color."),
    ("Drag an eel by either end into the hole of its colour.", "Arrastra una anguila por cualquier punta hasta el hueco de su color."),
    ("Scrape the soap. Each stroke takes off one layer.", "Raspa el jabón. Cada pasada saca una capa."),
    ("Flick the bumps off the soap. Each one takes two strokes.", "Saca los bultitos del jabón. Cada uno necesita dos pasadas."),
    ("Tap a jar, then another, to pour onto the same colour or into an empty jar.", "Toca un frasco y después otro para verter sobre el mismo color o en un frasco vacío."),
    ('aria-label="Block board"', 'aria-label="Tablero de bloques"'),
    ('aria-label="Jar of pods"', 'aria-label="Frasco de bolitas"'),
    ('aria-label="Sliding blocks board"', 'aria-label="Tablero de bloques que se deslizan"'),
    ('aria-label="Eels board"', 'aria-label="Tablero de anguilas"'),
    ('aria-label="A bar of soap"', 'aria-label="Un jabón"'),
    ('aria-label="A bar of soap with bumps"', 'aria-label="Un jabón con bultitos"'),
    ('aria-label="Jars"', 'aria-label="Frascos"'),
    ('<span id="n-fit">0 lines</span>', '<span id="n-fit">0 líneas</span>'),
    ('<span id="n-merge">0 merged</span>', '<span id="n-merge">0 juntadas</span>'),
    ('<span id="n-slide">Board 1</span>', '<span id="n-slide">Tablero 1</span>'),
    ('<span id="n-eels">Board 1</span>', '<span id="n-eels">Tablero 1</span>'),
    ('<span id="n-pour">Board 1</span>', '<span id="n-pour">Tablero 1</span>'),
    ('<span id="n-shave">Soap 1</span>', '<span id="n-shave">Jabón 1</span>'),
    ('<span id="n-bumps">Soap 1</span>', '<span id="n-bumps">Jabón 1</span>'),
    ('id="r-fit" type="button">Start over</button>', 'id="r-fit" type="button">Empezar de nuevo</button>'),
    ('id="r-merge" type="button">Empty the jar</button>', 'id="r-merge" type="button">Vaciar el frasco</button>'),
    ('id="r-slide" type="button">New board</button>', 'id="r-slide" type="button">Otro tablero</button>'),
    ('id="r-eels" type="button">New board</button>', 'id="r-eels" type="button">Otro tablero</button>'),
    ('id="r-pour" type="button">New board</button>', 'id="r-pour" type="button">Otro tablero</button>'),
    ('id="u-pour" type="button">Undo</button>', 'id="u-pour" type="button">Deshacer</button>'),
    ('id="r-shave" type="button">New soap</button>', 'id="r-shave" type="button">Otro jabón</button>'),
    ('id="r-bumps" type="button">New soap</button>', 'id="r-bumps" type="button">Otro jabón</button>'),
    ('aria-pressed="false">I\'d play this</button>', 'aria-pressed="false">Lo jugaría</button>'),
    ('on ? "✓ You\'d play this" : "I\'d play this"', 'on ? "✓ Lo jugarías" : "Lo jugaría"'),
    ('lines + (lines === 1 ? " line" : " lines")', 'lines + (lines === 1 ? " línea" : " líneas")'),
    ('merged + " merged"', 'merged + " juntadas"'),
    ('"Board " + board', '"Tablero " + board'),
    ('"Soap " + soap', '"Jabón " + soap'),
    ('"toast-fit", "Fresh board."', '"toast-fit", "Tablero nuevo."'),
    ('"toast-slide", "Clear."', '"toast-slide", "Listo."'),
    ('"toast-eels", "All home."', '"toast-eels", "Todas en casa."'),
    ('"toast-pour", "Sorted."', '"toast-pour", "Ordenado."'),
    ('"toast-merge", "Fresh jar."', '"toast-merge", "Frasco nuevo."'),
    ('"toast-shave", "Clean."', '"toast-shave", "Limpio."'),
    ('"toast-bumps", "Smooth."', '"toast-bumps", "Liso."'),
    ('toast("toast-merge", "Two stars.")', 'toast("toast-merge", "Dos estrellas.")'),
    ("path: next/\nalt: es/siguiente/", "path: es/siguiente/\nlang: es\nalt: next/"),
    # intro
    ("What should I build <em>next?</em>", "¿Qué agrego <em>ahora?</em>"),
    ('"✓ Your pick"', '"✓ Tu elección"'),
    ("This one?", "¿Esta?"),
    ("Which games would you <em>play?</em>", "¿Qué juegos <em>jugarías?</em>"),
    ("<p>For the minutes your hands want something to do. Try them, then mark up to three.</p>", "<p>Para esos minutos en que las manos buscan algo que hacer. Pruébalos y marca hasta tres.</p>"),
    ('id="hg-count">0 of 3</span>', 'id="hg-count">0 de 3</span>'),
    ('picks.length + " of " + GMAX', 'picks.length + " de " + GMAX'),
    ("And one of <em>these?</em>", "¿Y cuál de <em>estas?</em>"),
    ("<p>Pick one.</p>", "<p>Elige una.</p>"),
    ('"Undo"', '"Deshacer"'),
    ('<button class="nx-vote" type="button">Pick</button>', '<button class="nx-vote" type="button">Elegir</button>'),
    (': "Pick";', ': "Elegir";'),
    # 2 calendar
    ("A progress <em>calendar</em>", "Un calendario de <em>avances</em>"),
    ("<p>Each day gets a colour from what you logged. Stopping partway and riding out an urge both count.</p>",
     "<p>Cada día tiene un color según lo que registraste. Frenar a mitad y aguantar un impulso también cuentan.</p>"),
    ("<span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>",
     "<span>L</span><span>M</span><span>M</span><span>J</span><span>V</span><span>S</span><span>D</span>"),
    ('<p class="nx-hint">Tap a day to see what was logged.</p>', '<p class="nx-hint">Toca un día para ver qué se registró.</p>'),
    ('"No picks"', '"Sin pellizcos"'),
    ('"Stopped partway"', '"Frenado a mitad"'),
    ('"Rode out an urge"', '"Pasó un impulso"'),
    ('"Picked"', '"Hubo pellizcos"'),
    ('"Today"', '"Hoy"'),
    ('toLocaleDateString("en-GB"', 'toLocaleDateString("es"'),
    ('"No picks."', '"Sin pellizcos."'),
    ('(l.urges === 1 ? "An urge" : l.urges + " urges") + " passed."', '(l.urges === 1 ? "Pasó un impulso." : "Pasaron " + l.urges + " impulsos.")'),
    ('"A pick stopped partway."', '"Un pellizco frenado a mitad."'),
    ('other + (l.stopped ? " more" : "") + (other === 1 ? " pick." : " picks.")', 'other + (other === 1 ? " pellizco" : " pellizcos") + (l.stopped ? " más." : ".")'),
    ('" of 14 days count as progress."', '" de 14 días cuentan como avance."'),
    # 4 notebook
    ("A <em>notebook</em> to write it out", "Un <em>cuaderno</em> para escribirlo"),
    ("<p>For a thought that keeps coming back. Write it down and keep the page.</p>",
     "<p>Para un pensamiento que no se va. Lo escribes y guardas la página.</p>"),
    ('placeholder="What\'s on your mind? Two lines is enough." aria-label="Write a page"', 'placeholder="¿Qué tienes en mente? Con dos líneas basta." aria-label="Escribe una página"'),
    ('id="nx-keep" type="button" disabled>Keep it</button>', 'id="nx-keep" type="button" disabled>Guardar</button>'),
    ('aria-label="Delete this page"', 'aria-label="Borrar esta página"'),
    ("<span>Notebook</span>", "<span>Cuaderno</span>"),
    ("Only saved in this browser.", "Solo se guarda en este navegador."),
    ('"Keep it"', '"Guardar"'),
    ('"Done"', '"Listo"'),
    ('"Really delete"', '"Borrar de verdad"'),
    ('"Deleted"', '"Borrado"'),
    ('"Kept."', '"Guardada."'),
    ('"1 page"', '"1 página"'),
    ('" pages"', '" páginas"'),
    # thanks, feedback
    ("Thanks. I'll post which ones win.", "Gracias. Voy a publicar cuáles ganan."),
    ('href="{{store}}">Get Gentleskin</a>', 'href="{{store}}">Descargar Gentleskin</a>'),
    ("<h2>Anything else?</h2>", "<h2>¿Algo más?</h2>"),
    ("<p>Something missing, or something that bugs you.</p>", "<p>Algo que falta o algo que te molesta.</p>"),
    ('placeholder="Write anything" aria-label="Your message"', 'placeholder="Escribe lo que quieras" aria-label="Tu mensaje"'),
    ("<small>Anonymous.</small>", "<small>Anónimo.</small>"),
    ('id="nx-send" disabled>Send</button>', 'id="nx-send" disabled>Enviar</button>'),
    ("Got it. Thank you.", "Recibido. Gracias."),
    (">Write another</button>", ">Escribir otro</button>"),
    # analytics: same round and ids, marked as Spanish
    ('var ROUND = "2026-11c";', 'var ROUND = "2026-11c"; if (window.posthog) posthog.register({ next_lang: "es" });'),
    # the language switch: the English page sends Spanish browsers here; this one links back
    ('<a class="nx-lang" href="../es/siguiente/">Español</a>', '<a class="nx-lang" href="../../next/?lang=en">English</a>'),
    ("/* the language switch */ var NX_ES = true;", "/* the language switch */ var NX_ES = false;"),
]


def main():
    s = open(SRC).read()
    missing = [en for en, _ in PAIRS if en not in s]
    if missing:
        sys.exit("next_es.py: no longer on the English page:\n  " + "\n  ".join(missing))
    for en, es in PAIRS:
        s = s.replace(en, es)
    s = s.replace("<style>\n/* /next,", "<style>\n/* Generated by next_es.py from 70-next.html. Edit that and the table, not this. */\n/* /next,", 1)
    open(OUT, "w").write(s)


if __name__ == "__main__":
    main()
