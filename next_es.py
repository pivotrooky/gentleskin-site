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
    ("description: Six ideas for the Gentleskin skin picking app, working in your browser: feelings and tips, a calendar of progress, colouring for your hands, a notebook, self-care checks and a mirror timer. Try them, then vote for up to two.",
     "description: Seis ideas para Gentleskin, la app para la dermatilomanía, funcionando en tu navegador: emociones y consejos, un calendario de avances, colorear, una libreta, autocuidado y un temporizador para el espejo. Pruébalas y vota hasta dos."),
    ("path: next/\nalt: es/siguiente/", "path: es/siguiente/\nlang: es\nalt: next/"),
    # intro
    ("What should I build <em>next?</em>", "¿Qué agrego <em>ahora?</em>"),
    ("<p>Six ideas from people who pick. Each one works here.</p>", "<p>Seis ideas de personas que se pellizcan la piel. Todas funcionan aquí.</p>"),
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
    ("How you <em>felt</em>, and what helps", "Cómo te <em>sentiste</em>, y qué ayuda"),
    ("<p>Tap what you felt. Get one thing to try.</p>", "<p>Toca lo que sentiste. Te doy algo para probar.</p>"),
    ('<p class="nx-label">Before</p>', '<p class="nx-label">Antes</p>'),
    ('<p class="nx-label">After</p>', '<p class="nx-label">Después</p>'),
    ("Tap a feeling.", "Toca una emoción."),
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
    ("Good. What helped? Remember it for next time.", "Bien. ¿Qué ayudó? Recuérdalo para la próxima."),
    # 2 calendar
    ("A calendar of <em>progress</em>", "Un calendario de <em>avances</em>"),
    ("<p>Each day takes its colour from what you log. Stopping partway counts, and so does an urge you rode out.</p>",
     "<p>Cada día toma su color de lo que registras. Frenar a mitad de camino cuenta, y también un impulso que dejaste pasar.</p>"),
    ("<span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>",
     "<span>L</span><span>M</span><span>M</span><span>J</span><span>V</span><span>S</span><span>D</span>"),
    ('<p class="nx-label">Log today</p>', '<p class="nx-label">Registra hoy</p>'),
    ('"No picks"', '"Sin pellizcos"'),
    ('"Stopped partway"', '"Frenado a mitad"'),
    ('"Rode out an urge"', '"Pasó un impulso"'),
    ('"Picked"', '"Hubo pellizcos"'),
    ('"Today"', '"Hoy"'),
    ('toLocaleDateString("en-GB"', 'toLocaleDateString("es"'),
    ('"Nothing logged yet."', '"Nada registrado todavía."'),
    ('"No picks."', '"Sin pellizcos."'),
    ('(l.urges === 1 ? "An urge" : l.urges + " urges") + " passed."', '(l.urges === 1 ? "Pasó un impulso." : "Pasaron " + l.urges + " impulsos.")'),
    ('"A pick stopped partway."', '"Un pellizco frenado a mitad."'),
    ('other + (l.stopped ? " more" : "") + (other === 1 ? " pick." : " picks.")', 'other + (other === 1 ? " pellizco" : " pellizcos") + (l.stopped ? " más." : ".")'),
    ('" of 14 days count as progress."', '" de 14 días cuentan como avance."'),
    ('["picks", "A pick"]', '["picks", "Un pellizco"]'),
    ('["urges", "Urge passed"]', '["urges", "Pasó el impulso"]'),
    ('["reset", "Clear"]', '["reset", "Borrar"]'),
    # 3 colouring
    ("Colour it in, <em>with your finger</em>", "Colorear, <em>con el dedo</em>"),
    ("<p>Something for your hands when the urge comes. Keep the ones you like; new colours open up.</p>",
     "<p>Algo para tus manos cuando llega el impulso. Guarda los que te gusten; se van abriendo colores nuevos.</p>"),
    ('aria-label="A drawing to colour in with your finger or mouse"', 'aria-label="Un dibujo para colorear con el dedo o el mouse"'),
    ('id="nx-keepdraw" disabled>Keep it</button>', 'id="nx-keepdraw" disabled>Guardar</button>'),
    ('id="nx-cleardraw">Start over</button>', 'id="nx-cleardraw">Empezar de nuevo</button>'),
    ('aria-label="Your gallery"', 'aria-label="Tu galería"'),
    ('"Colour " + (cl_i + 1) : "Locked colour"', '"Color " + (cl_i + 1) : "Color bloqueado"'),
    ('"A drawing you coloured"', '"Un dibujo que coloreaste"'),
    ('"New colour."', '"Color nuevo."'),
    # 4 notebook
    ("A <em>notebook</em> to write it out", "Una <em>libreta</em> para escribirlo"),
    ("<p>When the urge is a thought that won't stop, write it out. Two lines is enough.</p>",
     "<p>Cuando el impulso es un pensamiento que no para, escríbelo. Con dos líneas alcanza.</p>"),
    ('placeholder="What\'s on your mind?" aria-label="Write a note"', 'placeholder="¿Qué tienes en la cabeza?" aria-label="Escribe una nota"'),
    ('id="nx-keep" type="button" disabled>Keep it</button>', 'id="nx-keep" type="button" disabled>Guardar</button>'),
    ("Nothing here is sent anywhere.", "Nada de esto se envía a ningún lado."),
    ('" · kept"', '" · guardado"'),
    # 5 self-care
    ("Self-care <em>checks</em>", "<em>Autocuidado</em> del día"),
    ("<p>Your own daily checks next to the picks: skincare, water, a plaster.</p>",
     "<p>Tus propios checks diarios junto a los pellizcos: skincare, agua, una curita.</p>"),
    ('addCheck("Skincare, morning"); addCheck("Skincare, night"); addCheck("Glasses of water", true); addCheck("Plaster on");',
     'addCheck("Skincare, mañana"); addCheck("Skincare, noche"); addCheck("Vasos de agua", true); addCheck("Curita puesta");'),
    ('"Done" : "Tap"', '"Listo" : "Tocar"'),
    ('r.textContent = "Tap"', 'r.textContent = "Tocar"'),
    # 6 mirror
    ("A <em>mirror</em> timer", "Un temporizador para el <em>espejo</em>"),
    ("<p>A few minutes at the mirror, not the whole night. Then the star tells you to step away.</p>",
     "<p>Unos minutos frente al espejo, no toda la noche. Después la estrella te dice que te alejes.</p>"),
    ('id="nx-mstart" type="button">Start</button>', 'id="nx-mstart" type="button">Empezar</button>'),
    ("Sped up for the demo.", "Acelerado para la demo."),
    ('"Checking is fine. Gentle hands."', '"Mirar está bien. Manos suaves."'),
    ('"Halfway. Notice your shoulders."', '"Mitad de tiempo. Fíjate en tus hombros."'),
    ('"Nearly time. Start to wrap up."', '"Ya casi. Ve terminando."'),
    ('"Time. Lights off, step out. You did it."', '"Listo. Apaga la luz y sal. Lo lograste."'),
    ('mstart.textContent = "Start"', 'mstart.textContent = "Empezar"'),
    ('mstart.textContent = "Stop"', 'mstart.textContent = "Parar"'),
    ('mstart.textContent = "Again"', 'mstart.textContent = "Otra vez"'),
    # thanks, feedback
    ("Thanks. I'll post which ones win.", "Gracias. Voy a publicar cuáles ganan."),
    ('href="{{store}}">Get Gentleskin</a>', 'href="{{store}}">Descargar Gentleskin</a>'),
    ("<h2>Anything else?</h2>", "<h2>¿Algo más?</h2>"),
    ("<p>Something missing, something that bugs you. I read every one.</p>", "<p>Algo que falta, algo que te molesta. Leo todos los mensajes.</p>"),
    ('placeholder="Write anything" aria-label="Your message"', 'placeholder="Escribe lo que quieras" aria-label="Tu mensaje"'),
    ("<small>Anonymous.</small>", "<small>Anónimo.</small>"),
    ('id="nx-send" disabled>Send</button>', 'id="nx-send" disabled>Enviar</button>'),
    ("Got it. Thank you.", "Recibido. Gracias."),
    (">Write another</button>", ">Escribir otro</button>"),
    # new and next
    ("New in the app, and <em>coming next</em>", "Nuevo en la app, y lo que <em>viene</em>"),
    ('<span class="nx-n">Next update</span>', '<span class="nx-n">Próxima versión</span>'),
    ("<b>Sounds for the wave</b><span>The sea, rain or brown noise while you ride it out. Off unless you turn it on.</span>",
     "<b>Sonidos para la ola</b><span>El mar, lluvia o ruido marrón mientras pasa. Apagado hasta que lo actives.</span>"),
    ('"▶ The sea"', '"▶ El mar"'),
    ('"▶ Rain"', '"▶ Lluvia"'),
    ('"▶ Brown noise"', '"▶ Ruido marrón"'),
    ('<span class="nx-n">In the app</span>', '<span class="nx-n">En la app</span>'),
    ("<b>Log from the Lock Screen</b><span>One tap on the widget logs it, without unlocking.</span>",
     "<b>Registrar desde la pantalla bloqueada</b><span>Un toque en el widget y queda registrado, sin desbloquear.</span>"),
    ("<b>Check-ins at your time</b><span>You choose the hour and the days.</span>",
     "<b>Avisos a tu hora</b><span>Tú eliges la hora y los días.</span>"),
    ("<b>What was going on</b><span>One optional tap when you log.</span>",
     "<b>Qué estaba pasando</b><span>Un toque opcional al registrar.</span>"),
    ("<b>Skin photos</b><span>Compare how your skin heals. They never leave your phone.</span>",
     "<b>Fotos de la piel</b><span>Compara cómo se cura tu piel. Nunca salen de tu teléfono.</span>"),
    ("<b>What helped</b><span>When an urge passes, tap what helped.</span>",
     "<b>Qué ayudó</b><span>Cuando pasa un impulso, toca qué ayudó.</span>"),
    ("<b>Your wave, your length</b><span>15 to 90 seconds, and how many bubbles to pop.</span>",
     "<b>Tu ola, tu duración</b><span>De 15 a 90 segundos, y cuántas burbujas reventar.</span>"),
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
