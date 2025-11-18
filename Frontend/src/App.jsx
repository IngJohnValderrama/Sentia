import "./App.css";
import { useState } from "react";

function App() {
  const [preview, setPreview] = useState(null);

  const [form, setForm] = useState({
    name: "",
    email: "",
    empresa: "",
    cargo: "",
    fechaNacimiento: "",
    edad: "",
    genero: "",
    emocion: "",
    energia: "",
    suenoCalidad: "",
    horasSueno: "",
    ejercicio: "",
    hobby: "",
    tipoInput: "",             
    textoIdentificacion: "",    
    foto: null,
    autorizacion: false,
  });

  // Manejo general de cambios
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    // Validación SOLO letras
    const soloLetras = /^[A-Za-zÁÉÍÓÚáéíóúÑñ ]*$/;

    if (["name", "empresa", "cargo"].includes(name)) {
      if (!soloLetras.test(value)) return;
    }

    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // Cargar imagen
  const handleImage = (e) => {
    const file = e.target.files[0];
    if (file) {
      setForm({ ...form, foto: file });
      setPreview(URL.createObjectURL(file));
    }
  };

  // Calcular edad automática
  const calcularEdad = (fecha) => {
    if (!fecha) return "";
    const hoy = new Date();
    const nac = new Date(fecha);
    let edad = hoy.getFullYear() - nac.getFullYear();
    return edad;
  };

  const handleFechaNacimiento = (e) => {
    const fecha = e.target.value;
    setForm({
      ...form,
      fechaNacimiento: fecha,
      edad: calcularEdad(fecha),
    });
  };

  // ENVIAR A N8N
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validación según la opción seleccionada
    if (form.tipoInput === "foto" && !form.foto) {
      alert("Debes tomar o subir una foto.");
      return;
    }

    if (form.tipoInput === "texto" && !form.textoIdentificacion.trim()) {
      alert("Debes escribir el texto de identificación.");
      return;
    }

    if (!form.autorizacion) {
      alert("Debes aceptar la autorización.");
      return;
    }

    // Crear FormData
    const data = new FormData();
    Object.entries(form).forEach(([key, value]) => {
      data.append(key, value);
    });

    try {
      const response = await fetch(
        "https://sentia-gtafbdh7e3ergfdy.eastus2-01.azurewebsites.net/webhook-test/webhook/formulario",
        {
          method: "POST",
          body: data,
        }
      );

      if (response.ok) {
        alert("Formulario enviado correctamente.");

        // Reset form
        setForm({
          name: "",
          email: "",
          empresa: "",
          cargo: "",
          fechaNacimiento: "",
          edad: "",
          genero: "",
          emocion: "",
          energia: "",
          suenoCalidad: "",
          horasSueno: "",
          ejercicio: "",
          hobby: "",
          tipoInput: "",
          textoIdentificacion: "",
          foto: null,
          autorizacion: false,
        });
        setPreview(null);
      } else {
        alert("Error al enviar los datos.");
      }
    } catch (error) {
      console.error("Error al conectar con n8n:", error);
      alert("Error de conexión con el servidor.");
    }
  };

  return (
    <div className="page">
      <header className="header">
        <div className="logo">
          <img src="logo_baner.png"alt="SentIA Logo" className="logo-img" />
        </div>
        <nav>
          <a>Inicio</a>
          <a>Acerca de nosotros</a>
          <a>Servicios</a>
          <a>Casos de éxito</a>
          <a>Blog</a>
        </nav>
        <button className="btn-header">Contacto</button>
      </header>

      <h1 className="title">Registro de Empleado</h1>
      <p className="subtitle">
        Ingresa la información del empleado y una fotografía para análisis emocional con IA.
      </p>

      <div className="card">
        {/* LEFT SIDE */}
        <div className="left-box">
          <h3>Información General</h3>
          <p>
            En SentIA, estamos comprometidos con el bienestar integral de los empleados. Al ingresar tu información y una fotografía, activas nuestro motor de Inteligencia Artificial de última generación. 
            Utilizando modelos avanzados, incluyendo tecnologías similares a Copilot y ChatGPT, nuestra IA es capaz de analizar los patrones faciales y las microexpresiones de la imagen para determinar tu estado emocional predominante (como alegría, tristeza o neutralidad). 
            Este análisis nos permite obtener una visión valiosa y objetiva sobre el clima emocional del equipo, asegurando que podamos ofrecer el apoyo y los recursos necesarios para un ambiente de trabajo positivo y productivo. Tu privacidad es fundamental; solo analizamos la emoción para mejorar tu experiencia.
          </p>

          <div className="contact-item">📍 Bogotá, Colombia</div>
          <div className="contact-item">✉️ jonatan.igua@uniminuto.edu.co</div>
          <div className="contact-item">✉️ carlos.mahecha-g@uniminuto.edu.co</div>
          <div className="contact-item">✉️ john.valderrama@uniminuto.edu.co</div>
          <div className="contact-item">✉️ juan.suarez-so@uniminuto.edu.co</div>
        </div>

        {/* FORMULARIO */}
        <form className="form" onSubmit={handleSubmit}>

          {/* NOMBRE + EMPRESA */}
          <div className="row">
            <div className="input-group">
              <label>Nombre completo *</label>
              <input name="name" value={form.name} onChange={handleChange} required />
            </div>

            <div className="input-group">
              <label>Empresa / Área *</label>
              <input name="empresa" value={form.empresa} onChange={handleChange} required />
            </div>
          </div>

          {/* CORREO */}
          <div className="input-group">
            <label>Correo electrónico *</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
            />
          </div>

          {/* CARGO + GENERO */}
          <div className="row">
            <div className="input-group">
              <label>Cargo *</label>
              <input name="cargo" value={form.cargo} onChange={handleChange} required />
            </div>

            <div className="input-group">
              <label>Género (opcional)</label>
              <select name="genero" value={form.genero} onChange={handleChange}>
                <option value="">Seleccione</option>
                <option value="Hombre">Hombre</option>
                <option value="Mujer">Mujer</option>
                <option value="No decir">Prefiero no decirlo</option>
              </select>
            </div>
          </div>

          {/* FECHA + EDAD */}
          <div className="row">
            <div className="input-group">
              <label>Fecha de nacimiento *</label>
              <input
                type="date"
                name="fechaNacimiento"
                value={form.fechaNacimiento}
                onChange={handleFechaNacimiento}
                required
              />
            </div>

            <div className="input-group">
              <label>Edad</label>
              <input value={form.edad} readOnly />
            </div>
          </div>

          {/* EMOCIÓN + ENERGÍA */}
          <div className="row">
            <div className="input-group">
              <label>¿Cómo te sientes hoy?</label>
              <select name="emocion" value={form.emocion} onChange={handleChange}>
                <option value="">Seleccione</option>
                <option value="Feliz">Feliz</option>
                <option value="Neutral">Neutral</option>
                <option value="Cansado">Cansado</option>
                <option value="Estresado">Estresado</option>
                <option value="Triste">Triste</option>
                <option value="Motivado">Motivado</option>
              </select>
            </div>

            <div className="input-group">
              <label>Nivel de energía (1 a 10)</label>
              <input
                type="number"
                name="energia"
                min="1"
                max="10"
                value={form.energia}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* SUEÑO */}
          <div className="row">
            <div className="input-group">
              <label>Calidad del sueño</label>
              <select name="suenoCalidad" value={form.suenoCalidad} onChange={handleChange}>
                <option value="">Seleccione</option>
                <option value="Mala">Mala</option>
                <option value="Regular">Regular</option>
                <option value="Buena">Buena</option>
                <option value="Muy buena">Muy buena</option>
              </select>
            </div>

            <div className="input-group">
              <label>Horas de sueño promedio</label>
              <input
                type="number"
                name="horasSueno"
                min="1"
                max="24"
                value={form.horasSueno}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* EJERCICIO */}
          <div className="input-group">
            <label>Frecuencia de ejercicio *</label>
            <select
              name="ejercicio"
              value={form.ejercicio}
              onChange={handleChange}
              required
            >
              <option value="">Seleccione</option>
              <option value="No hago">No hago</option>
              <option value="1-2 veces">1–2 veces por semana</option>
              <option value="3-4 veces">3–4 veces por semana</option>
              <option value="5+ veces">5+ veces</option>
            </select>
          </div>

          {/* HOBBY */}
          <div className="input-group">
            <label>¿Cuál es tu hobby o actividad favorita?</label>
            <input name="hobby" value={form.hobby} onChange={handleChange} />
          </div>

          {/* FOTO O TEXTO */}
          <div className="input-group">
            <label>Identificación del empleado *</label>

            <select
              name="tipoInput"
              value={form.tipoInput}
              onChange={handleChange}
              required
            >
              <option value="">Seleccione una opción</option>
              <option value="texto">Escribir texto</option>
              <option value="foto">Tomar / Subir foto</option>
            </select>

            {form.tipoInput === "texto" && (
              <input
                type="text"
                name="textoIdentificacion"
                placeholder="Escribe aquí..."
                value={form.textoIdentificacion}
                onChange={handleChange}
                required
              />
            )}

            {form.tipoInput === "foto" && (
              <>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleImage}
                  required
                />

                {preview && (
                  <img
                    src={preview}
                    alt="preview"
                    style={{
                      marginTop: "10px",
                      width: "120px",
                      borderRadius: "10px",
                    }}
                  />
                )}
              </>
            )}
          </div>

          {/* AUTORIZACIÓN */}
          <div className="input-group" style={{ display: "flex", gap: "10px" }}>
            <input
              type="checkbox"
              name="autorizacion"
              checked={form.autorizacion}
              onChange={handleChange}
              required
            />
            <label>
              Autorizo el uso de mi fotografía para análisis emocional con IA *
            </label>
          </div>

          <button className="btn-send">Enviar</button>
        </form>
      </div>
      <footer className="footer">
        <p>Copyright © 2025 SentIA - Todos los derechos reservados.</p>

        <div className="social-links">
          <a
            href="https://github.com/IngJohnValderrama/Sentia.git"
            target="_blank"
            rel="noopener noreferrer"
            className="social-icon github"
          >
            <svg viewBox="0 0 24 24">
              <path d="M12 .5C5.73.5.5 5.74.5 12.02c0 5.1 3.29 9.42 7.86 10.95.58.11.79-.25.79-.56v-1.98c-3.2.69-3.87-1.55-3.87-1.55-.53-1.36-1.3-1.72-1.3-1.72-1.06-.73.08-.72.08-.72 1.17.08 1.78 1.2 1.78 1.2 1.04 1.79 2.73 1.27 3.4.97.11-.76.41-1.27.75-1.57-2.56-.29-5.26-1.31-5.26-5.83 0-1.29.46-2.34 1.2-3.16-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.21a10.82 10.82 0 0 1 5.8 0c2.2-1.52 3.17-1.21 3.17-1.21.64 1.59.24 2.76.12 3.05.75.82 1.19 1.88 1.19 3.16 0 4.53-2.71 5.53-5.29 5.82.42.36.8 1.08.8 2.18v3.23c0 .31.21.68.8.56A10.53 10.53 0 0 0 23.5 12C23.5 5.73 18.28.5 12 .5z"/>
            </svg>
          </a>
        </div>
      </footer>
    </div>
  );
}

export default App;