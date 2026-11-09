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
    ("description: Four ideas for Gentleskin, the skin picking app: colouring, feelings and tips, a progress calendar and a notebook. Try them in your browser and vote for up to two.",
     "description: Cuatro ideas para Gentleskin, la app para la dermatilomanía: colorear, emociones y consejos, un calendario de avances y un cuaderno. Pruébalas en el navegador y vota hasta dos."),
    ("path: next/\nalt: es/siguiente/", "path: es/siguiente/\nlang: es\nalt: next/"),
    # intro
    ("What should I build <em>next?</em>", "¿Qué agrego <em>ahora?</em>"),
    ("<i>1</i>Try them", "<i>1</i>Pruébalas"),
    ("<i>2</i>Vote for up to two", "<i>2</i>Vota hasta dos"),
    ("<i>3</i>Tell me anything", "<i>3</i>Cuéntame lo que quieras"),
    ("You have 2 votes.", "Tienes 2 votos."),
    ("1 vote left.", "Te queda 1 voto."),
    ("Both votes used.", "Usaste los dos votos."),
    ('"✓ Your vote"', '"✓ Tu voto"'),
    ('"Two votes used"', '"Ya votaste dos"'),
    ("Want this one?", "¿Quieres esta?"),
    ('"Undo"', '"Deshacer"'),
    ('<button class="nx-vote" type="button">Vote</button>', '<button class="nx-vote" type="button">Votar</button>'),
    ('"Vote"', '"Votar"'),
    ('<span class="nx-n">Idea ', '<span class="nx-n">Idea '),
    # 1 feelings
    ("How you <em>felt</em>, and a tip", "Cómo te <em>sentiste</em>, y un consejo"),
    ("<p>After you log a pick, tap how you felt before and after. Then you get a tip for it.</p>",
     "<p>Después de registrar un pellizco, tocas cómo te sentías antes y después, y te sale un consejo para eso.</p>"),
    ("✓ Logged · 3 picks, face", "✓ Registrado · 3 pellizcos, cara"),
    ('"How were you feeling before?"', '"¿Cómo te sentías antes?"'),
    ('"And how do you feel now?"', '"¿Y cómo te sientes ahora?"'),
    ('id="nx-fback" hidden>‹ Back</button>', 'id="nx-fback" hidden>‹ Atrás</button>'),
    ('id="nx-fskip">Skip</button>', 'id="nx-fskip">Saltar</button>'),
    ("<b>Something to try</b>", "<b>Algo para probar</b>"),
    ('id="nx-fmore">Another one →</button>', 'id="nx-fmore">Otra idea →</button>'),
    ('id="nx-fagain">Start again</button>', 'id="nx-fagain">Empezar de nuevo</button>'),
    ('"Logged."', '"Registrado."'),
    ('"Angry at myself"', '"Enojo conmigo"'),
    ('"Anxious"', '"Ansiedad"'),
    ('"Bored"', '"Aburrimiento"'),
    ('"Frustrated"', '"Frustración"'),
    ('"Tense"', '"Tensión"'),
    ('"Restless"', '"Inquietud"'),
    ('"Guilty"', '"Culpa"'),
    ('"Relieved"', '"Alivio"'),
    ('"Calm"', '"Calma"'),
    ("Breathe out longer than you breathe in. Three times, then decide.", "Exhala más largo de lo que inhalas. Tres veces, y después decide."),
    ("Give your hands a job for two minutes: a fidget, a pen, an ice cube.", "Dales a tus manos algo que hacer por dos minutos: un fidget, un lápiz, un cubito de hielo."),
    ("Make a tight fist for ten seconds, then let it go. Twice.", "Aprieta el puño diez segundos y suéltalo. Dos veces."),
    ("Drop your shoulders and unclench your jaw. Notice where your hands are.", "Baja los hombros y afloja la mandíbula. Fíjate dónde están tus manos."),
    ("Stand up and walk to another room. The urge often stays behind.", "Levántate y ve a otra habitación. Muchas veces el impulso se queda atrás."),
    ("One pick doesn't undo the good days. Wash it, cover it, leave it.", "Un pellizco no borra los días buenos. Lávalo, cúbrelo, déjalo."),
    ("Notice what led here. Next time you can catch it a little earlier.", "Fíjate qué te trajo hasta aquí. La próxima vez puedes frenarlo un poco antes."),
    ("Talk to yourself the way you'd talk to a friend who picks.", "Háblate como le hablarías a alguien querido que se pellizca."),
    ("Note what helped, so it's there next time.", "Anota qué ayudó, para tenerlo la próxima vez."),
    ("Name five things you can see. It pulls attention out of your fingertips.", "Nombra cinco cosas que ves. Saca la atención de la punta de los dedos."),
    ("Wear something with texture: a ring, a hair tie, soft gloves.", "Ponte algo con textura: un anillo, una gomita, guantes suaves."),
    ("Cold water on your hands and face for thirty seconds.", "Agua fría en las manos y la cara por treinta segundos."),
    ("Cover the spot with a bandage. Out of sight is easier to leave.", "Cubre la zona con una curita. Lo que no ves es más fácil de dejar."),
    ("Write one line about what came before. Patterns show up later.", "Escribe una línea sobre lo que pasó antes. Los patrones aparecen después."),
    ("Slow the next ten minutes down: a glass of water, a window, a breath.", "Baja el ritmo los próximos diez minutos: un vaso de agua, una ventana, una respiración."),
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
    # 1 colouring
    ("Colour it in, <em>inside the lines</em>", "Colorea <em>sin salirte de las líneas</em>"),
    ("<p>Something for your hands to do.</p>", "<p>Algo para hacer con las manos.</p>"),
    ("<li>Paint with your finger. The colour stays inside the shape you started in, even if you scribble over a line.</li>",
     "<li>Pinta con el dedo. El color se queda dentro de la forma donde empezaste, aunque garabatees encima de una línea.</li>"),
    ("<li>Or tap a shape to fill it.</li>", "<li>O toca una forma para rellenarla.</li>"),
    ("<li>Finished pages go in a gallery, and each one unlocks a new colour.</li>",
     "<li>Las páginas terminadas quedan en una galería, y cada una desbloquea un color nuevo.</li>"),
    ('aria-label="A page to colour in with your finger or mouse"', 'aria-label="Una página para colorear con el dedo o el mouse"'),
    ("Try scribbling over a line.", "Prueba garabatear sobre una línea."),
    ('aria-label="Tools"', 'aria-label="Herramientas"'),
    ('aria-label="Undo"', 'aria-label="Deshacer"'),
    ('aria-label="Brush size"', 'aria-label="Tamaño del pincel"'),
    ('aria-label="Colours"', 'aria-label="Colores"'),
    ('id="nx-keepdraw" disabled>Keep it</button>', 'id="nx-keepdraw" disabled>Guardar</button>'),
    ('<p class="nx-label">Pages</p>', '<p class="nx-label">Páginas</p>'),
    ('id="nx-gallery-l" hidden>Your gallery</p>', 'id="nx-gallery-l" hidden>Tu galería</p>'),
    ('aria-label="Your gallery"', 'aria-label="Tu galería"'),
    ('starfish: "Starfish", sea: "The sea", shell: "Shell", plant: "Plant", flower: "Flower"',
     'starfish: "Estrella de mar", sea: "El mar", shell: "Concha", plant: "Planta", flower: "Flor"'),
    ('brush: "Brush", fill: "Tap to fill", eraser: "Eraser"', 'brush: "Pincel", fill: "Rellenar", eraser: "Goma"'),
    ('["Thin", "Medium", "Thick"][i] + " brush"', '"Pincel " + ["fino", "medio", "grueso"][i]'),
    ('"Each page you keep opens a new colour."', '"Cada página que guardas abre un color nuevo."'),
    ('"Colour " + (i + 1) : "Locked colour"', '"Color " + (i + 1) : "Color bloqueado"'),
    ('", kept"', '", guardada"'),
    ('"Kept in your gallery. A new colour."', '"Guardada en tu galería. Un color nuevo."'),
    ('"Kept in your gallery."', '"Guardada en tu galería."'),
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
    # new and next
    ("In the app, and <em>next</em>", "En la app, y lo <em>próximo</em>"),
    ('<span class="nx-n">Next update</span>', '<span class="nx-n">Próxima versión</span>'),
    ("<b>Sounds for the wave</b><span>Sea, rain or brown noise during the wave. Off by default.</span>",
     "<b>Sonidos para la ola</b><span>Mar, lluvia o ruido marrón durante la ola. Vienen apagados.</span>"),
    ('"▶ The sea"', '"▶ El mar"'),
    ('"▶ Rain"', '"▶ Lluvia"'),
    ('"▶ Brown noise"', '"▶ Ruido marrón"'),
    ('<span class="nx-n">In the app</span>', '<span class="nx-n">En la app</span>'),
    ("<b>Log from the Lock Screen</b><span>One tap on the widget, without unlocking.</span>",
     "<b>Registrar desde la pantalla bloqueada</b><span>Un toque en el widget, sin desbloquear.</span>"),
    ("<b>Check-ins at your time</b><span>Pick the hour and the days.</span>",
     "<b>Avisos a tu hora</b><span>Eliges la hora y los días.</span>"),
    ("<b>What was going on</b><span>One optional tap when you log.</span>",
     "<b>Qué estaba pasando</b><span>Un toque opcional al registrar.</span>"),
    ("<b>Skin photos</b><span>To compare how it heals. They stay on your phone.</span>",
     "<b>Fotos de la piel</b><span>Para comparar cómo se cura. Quedan en tu teléfono.</span>"),
    ("<b>What helped</b><span>When an urge passes, tap what helped.</span>",
     "<b>Qué ayudó</b><span>Cuando pasa un impulso, toca qué ayudó.</span>"),
    ("<b>Wave length</b><span>15 to 90 seconds, and how many bubbles to pop.</span>",
     "<b>Duración de la ola</b><span>De 15 a 90 segundos, y cuántas burbujas reventar.</span>"),
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
